![header](https://capsule-render.vercel.app/api?type=waving&color=0:bee1e8,100:ddc7fc&height=250&section=header&text=인물%20기반%20예능%20숏폼%20영상%20생성기%2c%20%23눈%23사람&fontColor=262626&desc=예능%20영상에서%20원하는%20인물의%20하이라이트%20쇼츠를%20간편하게%20생성할%20수%20있습니다.&fontAlignY=35&descAlignY=52&fontSize=40&descSize=20&animation=fadeIn)

<img src="https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=Python&logoColor=white"> <img src="https://img.shields.io/badge/JavaScript-F7DF1E?style=for-the-badge&logo=JavaScript&logoColor=black"> <img src="https://img.shields.io/badge/Jupyter-F37626?style=for-the-badge&logo=Jupyter&logoColor=white">  
<img src="https://img.shields.io/badge/PyTorch-EE4C2C?style=for-the-badge&logo=PyTorch&logoColor=white"> <img src="https://img.shields.io/badge/Dlib-008000?style=for-the-badge&logo=Dlib&logoColor=white"> <img src="https://img.shields.io/badge/OpenCV-5C3EE8?style=for-the-badge&logo=OpenCV&logoColor=white"> <img src="https://img.shields.io/badge/FFmpeg-007808?style=for-the-badge&logo=FFmpeg&logoColor=white">  
<img src="https://img.shields.io/badge/FastAPI-009688?style=for-the-badge&logo=FastAPI&logoColor=white"> <img src="https://img.shields.io/badge/react-61DAFB?style=for-the-badge&logo=react&logoColor=black">

<br>


## Members

> Hi! This is Team Snowman

|                                                             Hajun Kim                                                             |                                                            Minsoo Song                                                            |                                                            Junkyo Shim                                                            |                                                            Sengri Yoo                                                            |                                                           Changjin Lee                                                            |                                                          Yeongwoo Jeong                                                           |
| :-------------------------------------------------------------------------------------------------------------------------------: | :-------------------------------------------------------------------------------------------------------------------------------: | :-------------------------------------------------------------------------------------------------------------------------------: | :------------------------------------------------------------------------------------------------------------------------------: | :-------------------------------------------------------------------------------------------------------------------------------: | :-------------------------------------------------------------------------------------------------------------------------------: |
| ![눈사람_김하준](https://user-images.githubusercontent.com/43572543/164686306-5f2618e9-90b0-4446-a193-1c8e7f1d77ad.png) | ![눈사람_송민수](https://user-images.githubusercontent.com/43572543/164686145-4030fd4f-bdd1-4dfa-9495-16d7c7689731.png) | ![눈사람_심준교](https://user-images.githubusercontent.com/43572543/164686612-d221b3c9-8895-4ac4-af4e-385412afe541.png) | ![눈사람_유승리](https://user-images.githubusercontent.com/43572543/164686476-0b3374d4-1f00-419c-ae5a-ecd37227c1ef.png) | ![눈사람_이창진](https://user-images.githubusercontent.com/43572543/164686491-c7acc30f-7175-4ce5-b2ea-46059857d955.png) | ![눈사람_전영우](https://user-images.githubusercontent.com/43572543/164686498-d251b498-b3fa-4c3c-b5f9-7cd2b62ed58b.png) |
|                                                            `Modeling`                                                             |                                                             `Serving`                                                             |                                                            `Modeling`                                                             |                                                            `Serving`                                                             |                                                            `Modeling`                                                             |                                                            `Modeling`                                                             |
|                                               [GitHub](https://github.com/HajunKim)                                               |                                               [GitHub](https://github.com/sooya233)                                               |                                             [GitHub](https://github.com/Shimjoonkyo)                                              |                                             [GitHub](https://github.com/seungriyou)                                              |                                              [GitHub](https://github.com/noisrucer)                                               |                                               [GitHub](https://github.com/wowo0709)                                               |

<br>

## Introduction

### Background

- Entertainment programs are edited around guests and uploaded as highlight reels to various platforms, but the editing process that requires professional personnel is costly and time-consuming.
- The recent trend in video consumption is short-form videos, which are about 1 minute or less and easily enjoyable. When edited into short-form videos compared to the same video, there are more opportunities for exposure and more views on various platforms.

### Contribution

- Automating the editing process that was previously done by professional personnel minimizes time and cost.
- A person-based editing methodology that meets the needs of users who want to see videos centered around guests is proposed.
- A video editing methodology that considers both the characteristics of entertainment and short-form videos is proposed.

<br>

<img width="1458" alt="전체_flow" src="https://user-images.githubusercontent.com/43572543/173187784-3291c4ea-d833-43a7-a333-d3285a3a0ec2.png">

<br>

## System Flow

### [1] Perform Person Clustering and Laughter Detection when uploading videos

<img src="https://user-images.githubusercontent.com/43572543/173084985-387484db-51f2-46a3-a1c4-f3c4d9b3b078.gif" width="600" />

#### Scene Detection & Person Clustering

- After detecting the scenes where the screen changes, the individuals appearing in the video are identified using face and clothing information.
- eature vectors for face landmarks and clothing are normalized, concatenated, and hierarchical agglomerative clustering (HAC) is performed.
- Clustering performance is further improved through various post-processing methods, and the clearest photo is selected for each person cluster and presented to the user.

#### Laughter Detection

- Laughter timeline is extracted from the audio files of entertainment videos.
- Laughter segments with short timelines are merged, and each timeline is subjected to [-15 seconds, +0.5 seconds] operation to create a short-form video candidate that includes context.
- The laughter detection server is separate and runs concurrently with other operations.

<br>

### [2] When user selects a person, generate highlight clips by person-recognition.

<img src="https://user-images.githubusercontent.com/43572543/173085027-cf4954da-8bc7-4b9f-92c9-afeb41634e7c.gif" width="600" />

#### Person Recognition

- Person timeline is also extracted using the face and clothing information of the individual selected by the user, and the average value of the feature vector obtained from clustering is used.

#### Final Timeline & Interest Estimation

- The final timeline, which is a short-form video candidate in which the target individual appears for a certain proportion or more, is calculated by combining the laughter timeline and the person timeline. Short-form videos are then generated.
- For each final timeline, interest is calculated by a weighted sum of the following three features:
  ```
  (1) Average length of laughter in the video
  (2) Average volume of laughter in the video
  (3) Proportion of appearance of the individual.
  ```

<br>

### [3] Generated highlight clips and Download

> Generated clips are sorted by interest.

<img src="https://user-images.githubusercontent.com/43572543/173085034-3700f373-707e-411c-a89c-bec6abea7c1f.gif" width="600" />

<br>

## System Architecture

<img width="1466" alt="시스템_구성도" src="https://user-images.githubusercontent.com/43572543/173294290-2a8af4fd-6672-4de1-af3c-e839dd21e247.png">

<br>

## More Information

### Modeling

[>> LINK](https://github.com/boostcampaitech3/final-project-level3-cv-10/tree/main/model)

### Serving

[>> LINK](https://github.com/boostcampaitech3/final-project-level3-cv-10/tree/main/serving)

### Document & Demo

| Type          | Link                                                                                                                                                                                                                                                                                                                                  |
| ------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| WrapUp Report | [>> PDF](<https://github.com/boostcampaitech3/final-project-level3-cv-10/blob/main/%E1%84%8E%E1%85%AC%E1%84%8C%E1%85%A9%E1%86%BC%E1%84%91%E1%85%B3%E1%84%85%E1%85%A9%E1%84%8C%E1%85%A6%E1%86%A8%E1%84%90%E1%85%B3_CV_%E1%84%90%E1%85%B5%E1%86%B7%20%E1%84%85%E1%85%B5%E1%84%91%E1%85%A9%E1%84%90%E1%85%B3(10%E1%84%8C%E1%85%A9).pdf>) |
| Presentation  | [>> PDF](https://drive.google.com/file/d/1iSQKfMrLj3v85jroaw_M6OYMAwXFohmc/view?usp=sharing)                                                                                                                                                                                                                                          |
| Demo          | [>> VIDEO](https://drive.google.com/file/d/1zMjFBrJvRXcn8x8K6XqoiAigqCGYR396/view?usp=sharing)                                                                                                                                                                                                                                        |

<br>

## Reference

### Paper

- Gillick, Jon, et al. "Robust Laughter Detection in Noisy Environments." Proc. Interspeech 2021 (2021): 2481-2485. [[PAPER]](https://www.isca-speech.org/archive/pdfs/interspeech_2021/gillick21_interspeech.pdf) [[CODE]](https://github.com/jrgillick/laughter-detection)
- Brown, Andrew, Vicky Kalogeiton, and Andrew Zisserman. "Face, body, voice: Video person-clustering with multiple modalities." Proceedings of the IEEE/CVF International Conference on Computer Vision. 2021. [[PAPER]](https://arxiv.org/pdf/2105.09939.pdf)
- Robertson, David J., Robin SS Kramer, and A. Mike Burton. "Face averages enhance user recognition for smartphone security." PloS one 10.3 (2015): e0119460. [[PAPER]](https://journals.plos.org/plosone/article/file?id=10.1371/journal.pone.0119460&type=printable)
- Davies, David L., and Donald W. Bouldin. "A cluster separation measure." IEEE transactions on pattern analysis and machine intelligence 2 (1979): 224-227. [[PAPER]](https://www.researchgate.net/publication/224377470_A_Cluster_Separation_Measure)
- Komatsu, Kazuaki., Kazutaka Shimada, and Tsutomu Endo. "A person identification method using facial, clothing and time features." (2017) [[PAPER]](http://www.pluto.ai.kyutech.ac.jp/~shimada/paper/IWACIIIKomatsu.pdf)
- El Khoury, Elie, Christine Sénac, and Philippe Joly. "Face-and-clothing based people clustering in video content." Proceedings of the international conference on Multimedia information retrieval. 2010. [[PAPER]](https://dl.acm.org/doi/10.1145/1743384.1743435)
- Yang, Saelyne, et al. "CatchLive: Real-time Summarization of Live Streams with Stream Content and Interaction Data." CHI Conference on Human Factors in Computing Systems. 2022. [[PAPER]](https://kixlab.github.io/website-files/2022/chi2022-CatchLive-paper.pdf)

### Open Source

- Face Recognition [[CODE]](https://github.com/ageitgey/face_recognition)
- Unknown Face Classifier [[CODE]](https://github.com/ukayzm/opencv/tree/master/unknown_face_classifier)
- Image Cluster [[CODE]](https://github.com/elcorto/imagecluster)

<br>

![Footer](https://capsule-render.vercel.app/api?type=waving&color=0:bee1e8,100:ddc7fc&height=200&section=footer)
