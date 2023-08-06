from functools import partial

import numpy as np
import torch
from timm.models.efficientnet import tf_efficientnet_b7_ns
from torch import nn
from torch.nn.modules.dropout import Dropout
from torch.nn.modules.linear import Linear
from torch.nn.modules.pooling import AdaptiveAvgPool2d
#from facebook_deit import deit_base_patch16_224, deit_distill_large_patch16_384, deit_distill_large_patch32_384
#from taming_transformer import Decoder, VUNet, ActNorm
import functools
#from vit_pytorch.distill import DistillableViT, DistillWrapper, DistillableEfficientViT
import re

encoder_params = {
    "tf_efficientnet_b7_ns": {
        "features": 2560,
        "init_op": partial(tf_efficientnet_b7_ns, pretrained=True, drop_path_rate=0.2)
    }
}

class GlobalWeightedAvgPool2d(nn.Module):
    """
    Global Weighted Average Pooling from paper "Global Weighted Average
    Pooling Bridges Pixel-level Localization and Image-level Classification"
    """

    def __init__(self, features: int, flatten=False):
        super().__init__()
        self.conv = nn.Conv2d(features, 1, kernel_size=1, bias=True)
        self.flatten = flatten

    def fscore(self, x):
        m = self.conv(x)
        m = m.sigmoid().exp()
        return m

    def norm(self, x: torch.Tensor):
        return x / x.sum(dim=[2, 3], keepdim=True)

    def forward(self, x):
        input_x = x
        x = self.fscore(x)
        x = self.norm(x)
        x = x * input_x
        x = x.sum(dim=[2, 3], keepdim=not self.flatten)
        return x


class DeepFakeClassifier(nn.Module):
    def __init__(self, encoder, dropout_rate=0.0) -> None:
        super().__init__()
        self.encoder = encoder_params[encoder]["init_op"]()
        self.avg_pool = AdaptiveAvgPool2d((1, 1))
        self.dropout = Dropout(dropout_rate)
        self.fc = Linear(encoder_params[encoder]["features"], 1)

    def forward(self, x):
        x = self.encoder.forward_features(x)
        x = self.avg_pool(x).flatten(1)
        x = self.dropout(x)
        x = self.fc(x)
        return x

class NLayerDiscriminator(nn.Module):
    """Defines a PatchGAN discriminator as in Pix2Pix
        --> see https://github.com/junyanz/pytorch-CycleGAN-and-pix2pix/blob/master/models/networks.py
    """
    def __init__(self, input_nc=3, ndf=64, n_layers=3, use_actnorm=False):
        """Construct a PatchGAN discriminator
        Parameters:
            input_nc (int)  -- the number of channels in input images
            ndf (int)       -- the number of filters in the last conv layer
            n_layers (int)  -- the number of conv layers in the discriminator
            norm_layer      -- normalization layer
        """
        super(NLayerDiscriminator, self).__init__()
        if not use_actnorm:
            norm_layer = nn.BatchNorm2d
        else:
            norm_layer = ActNorm
        if type(norm_layer) == functools.partial:  # no need to use bias as BatchNorm2d has affine parameters
            use_bias = norm_layer.func != nn.BatchNorm2d
        else:
            use_bias = norm_layer != nn.BatchNorm2d

        kw = 4
        padw = 1
        sequence = [nn.Conv2d(input_nc, ndf, kernel_size=kw, stride=2, padding=padw), nn.LeakyReLU(0.2, True)]
        nf_mult = 1
        nf_mult_prev = 1
        for n in range(1, n_layers):  # gradually increase the number of filters
            nf_mult_prev = nf_mult
            nf_mult = min(2 ** n, 8)
            sequence += [
                nn.Conv2d(ndf * nf_mult_prev, ndf * nf_mult, kernel_size=kw, stride=2, padding=padw, bias=use_bias),
                norm_layer(ndf * nf_mult),
                nn.LeakyReLU(0.2, True)
            ]

        nf_mult_prev = nf_mult
        nf_mult = min(2 ** n_layers, 8)
        sequence += [
            nn.Conv2d(ndf * nf_mult_prev, ndf * nf_mult, kernel_size=kw, stride=1, padding=padw, bias=use_bias),
            norm_layer(ndf * nf_mult),
            nn.LeakyReLU(0.2, True)
        ]

        sequence += [
            nn.Conv2d(ndf * nf_mult, 1, kernel_size=kw, stride=1, padding=padw)]  # output 1 channel prediction map
        self.main = nn.Sequential(*sequence)

    def forward(self, input):
        """Standard forward."""
        return self.main(input)

class Discriminator(nn.Module):
    def __init__(self, channel = 3, n_strided=6):
        super(Discriminator, self).__init__()
        self.main = nn.Sequential(
            nn.Conv2d(channel, 64, 4, 2, 1, bias=False), #384 -> 192
            nn.LeakyReLU(0.2, inplace=True),
            nn.Conv2d(64, 128, 4, 2, 1, bias=False),  #192->96
            nn.BatchNorm2d(128),
            nn.LeakyReLU(0.2, inplace=True),
            nn.Conv2d(128, 256, 4, 2, 1, bias=False), # 96->48
            nn.BatchNorm2d(256),
            nn.LeakyReLU(0.2, inplace=True),
            nn.Conv2d(256, 512, 4, 2, 1, bias=False), #48->24
            nn.BatchNorm2d(512),
            nn.LeakyReLU(0.2, inplace=True),
            nn.Conv2d(512, 1024, 4, 2, 1, bias=False), #24->12
            nn.BatchNorm2d(1024),
            nn.LeakyReLU(0.2, inplace=True),
            nn.Conv2d(1024, 1, 4, 2, 1, bias=False), #12->6
        )
        self.last = nn.Sequential(
            #(B, 6*6)
            nn.Linear(6*6, 1),
            #nn.Sigmoid()
        )

        def discriminator_block(in_filters, out_filters):
            layers = [nn.Conv2d(in_filters, out_filters, 4, stride=2, padding=1), nn.LeakyReLU(0.01)]
            return layers

        layers = discriminator_block(channel, 32)
        curr_dim = 32
        for _ in range(n_strided-1):
            layers.extend(discriminator_block(curr_dim, curr_dim*2))
            curr_dim *= 2
        layers.extend(discriminator_block(curr_dim,curr_dim))
        self.model = nn.Sequential(*layers)
        self.out1 = nn.Conv2d(curr_dim, 1, 3, stride=1, padding=0, bias=False)
    def forward(self, x):
        #x = self.main(x).view(-1,6*6)
        feature_repr = self.model(x)
        x = self.out1(feature_repr)
        return x.view(-1, 1)#self.last(x)

##############################
#           RESNET
##############################


class ResidualBlock(nn.Module):
    def __init__(self, in_features):
        super(ResidualBlock, self).__init__()

        conv_block = [
            nn.Conv2d(in_features, in_features, 3, stride=1, padding=1, bias=False),
            nn.InstanceNorm2d(in_features, affine=True, track_running_stats=True),
            nn.ReLU(inplace=True),
            nn.Conv2d(in_features, in_features, 3, stride=1, padding=1, bias=False),
            nn.InstanceNorm2d(in_features, affine=True, track_running_stats=True),
        ]

        self.conv_block = nn.Sequential(*conv_block)

    def forward(self, x):
        return x + self.conv_block(x)

class Pre_training(nn.Module):
    def __init__(self, encoder, channel=3, res_blocks=5, dropout_rate=0.0, patch_size=16) -> None:
        super().__init__()
        self.encoder = encoder_params[encoder]["init_op"]()
        self.emb_ch = encoder_params[encoder]["features"]

        '''
        self.teacher = DeepFakeClassifier(encoder="tf_efficientnet_b7_ns").to("cuda")
        checkpoint = torch.load('weights/final_111_DeepFakeClassifier_tf_efficientnet_b7_ns_0_36', map_location='cpu')
        state_dict = checkpoint.get("state_dict", checkpoint)
        self.teacher.load_state_dict({re.sub("^module.", "", k): v for k, v in state_dict.items()}, strict=False)
        '''
        '''
        self.deconv = nn.Sequential(
            nn.Conv2d(self.emb_ch, self.emb_ch//2, kernel_size=3, stride=1, padding=1),
            nn.BatchNorm2d(self.emb_ch // 2),
            nn.ReLU(True),
            nn.Conv2d(self.emb_ch//2, self.emb_ch //4, kernel_size=3, stride=1, padding=1),
            nn.BatchNorm2d(self.emb_ch //4),
            nn.ReLU(True),
        )
        '''
        '''
        self.deconv = nn.Sequential(
            nn.ConvTranspose2d(self.emb_ch, self.emb_ch//2 , kernel_size=4, stride=2, padding=1, bias=False),
            nn.BatchNorm2d(self.emb_ch//2),
            nn.ReLU(True),
            nn.ConvTranspose2d(self.emb_ch//2, self.emb_ch // 4, kernel_size=4, stride=2, padding=1, bias=False),
            nn.BatchNorm2d(self.emb_ch // 4),
            nn.ReLU(True),
            nn.ConvTranspose2d(self.emb_ch//4, self.emb_ch // 8, kernel_size=4, stride=2, padding=1, bias=False),
            nn.BatchNorm2d(self.emb_ch // 8),
            nn.ReLU(True),
            nn.ConvTranspose2d(self.emb_ch//8, channel, kernel_size=4, stride=2, padding=1, bias=False),
            nn.Tanh()
        )
        '''
        #self.deconv = nn.ConvTranspose2d(self.emb_ch, 3, kernel_size=16, stride=16)
        #self.decoder = Decoder(double_z = False, z_channels = 1024, resolution= 384, in_channels=3, out_ch=3, ch=64
        #                       , ch_mult=[1,1,2,2], num_res_blocks = 0, attn_resolutions=[16], dropout=0.0)
        #nn.ConvTranspose2d(encoder_params[encoder]["features"], channel, kernel_size=patch_size, stride=patch_size)
        channels = self.emb_ch
        model = [
            nn.ConvTranspose2d(channels, channels, 7, stride=1, padding=3, bias=False),
            nn.InstanceNorm2d(channels, affine=True, track_running_stats=True),
            nn.ReLU(inplace=True),
        ]
        curr_dim = channels

        for _ in range(2):
            model+=[
                nn.ConvTranspose2d(curr_dim, curr_dim//2, 4, stride=2, padding=1, bias=False),
                nn.InstanceNorm2d(curr_dim//2, affine=True, track_running_stats=True),
                nn.ReLU(inplace=True),
            ]
            curr_dim //= 2

        #Residual blocks
        for _ in range(res_blocks):
            model += [ResidualBlock(curr_dim)]
        #Upsampling
        for _ in range(2):
            model += [
                nn.ConvTranspose2d(curr_dim, curr_dim//2, 4, stride=2, padding=1, bias=False),
                nn.InstanceNorm2d(curr_dim//2, affine=True, track_running_stats=True),
                nn.ReLU(inplace=True),
            ]
            curr_dim = curr_dim //2
        #output layer
        model += [nn.Conv2d(curr_dim, channel, 7, stride=1, padding=3), nn.Tanh()]
        self.model = nn.Sequential(*model)
        self.fc = Linear(encoder_params[encoder]["features"], 1)
        self.dropout = Dropout(dropout_rate)
    '''
    def generator(self, x, freeze):
        if freeze:
            with torch.no_grad():
                _, z = self.encoder.pre_training(x)
            for param in self.encoder.parameters():
                param.requires_grad = False
        else:
            #with torch.enable_grad():
            for param in self.encoder.parameters():
                param.requires_grad = True
            _, z = self.encoder.pre_training(x)
        x = self.model(z)
        return x
    def discriminator(self, x ,freeze):
        if freeze:
            with torch.no_grad():
                cls_token, _ = self.encoder.pre_training(x)
            for param in self.encoder.parameters():
                param.requires_grad = False
        else:
            #with torch.enable_grad():
            for param in self.encoder.parameters():
                param.requires_grad = True
            cls_token, _ = self.encoder.pre_training(x)
        x = self.dropout(cls_token)
        cls = self.fc(x)
        return cls
    '''
    def get_class(self,x):
        for param in self.teacher.parameters():
            param.requires_grad = False
        teacher_logits = self.teacher(x)
        return teacher_logits

    def forward(self, x):
        cls_token, z = self.encoder.pre_training(x)
        #with torch.no_grad():
        #    teacher_logits = self.teacher(x)
        #x = self.deconv(x)
        #x = self.decoder(x)
        #cls = self.dropout(cls_token)
        #cls_token = self.fc(cls)

        x = self.model(z)
        return x#, cls_token, teacher_logits#, labels

class DeepFakeClassifierGWAP(nn.Module):
    def __init__(self, encoder, dropout_rate=0.5) -> None:
        super().__init__()
        self.encoder = encoder_params[encoder]["init_op"]()
        self.avg_pool = GlobalWeightedAvgPool2d(encoder_params[encoder]["features"])
        self.dropout = Dropout(dropout_rate)
        self.fc = Linear(encoder_params[encoder]["features"], 1)

    def forward(self, x):
        x = self.encoder.forward_features(x)
        x = self.avg_pool(x).flatten(1)
        x = self.dropout(x)
        x = self.fc(x)
        return x
