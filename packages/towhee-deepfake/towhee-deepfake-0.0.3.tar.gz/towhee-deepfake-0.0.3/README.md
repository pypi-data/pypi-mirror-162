# Deepfake

*author: Zhuoran Yu*

<br />

## Description

Deepfake techniques, which present realistic AI-generated videos of people doing and saying fictional things, have the potential to have a significant impact on how people determine the legitimacy of information presented online.

This operator predicts the probability of a fake video for a given video.This is an adaptation from [DeepfakeDetection](https://github.com/smu-ivpl/DeepfakeDetection).

<br />

## Code Example

Load videos from path '/home/test_video'
and use deepfake operator to predict the probabilities of fake videos.


```python
import towhee
(
    towhee.glob['path']('/home/test_video')
          .deepfake['path', 'scores']()
          .select['path', 'scores']()
          .show()
)
```

<img src="./deepfake.png" height="100px"/>

```shell
[0.9893, 0.9097]
```

<br />

## Interface

A deepfake operator takes videos' paths as input.
It predicts the probabilities of fake videos.The higher the score, the higher the probability of it being a fake video.(It can be considered to be a fake video with score higher than 0.5)

**Parameters:**

***filepath:*** *str*

Absolute address of the test videos.


**Returns:** *list*

The probabilities of videos being fake ones.