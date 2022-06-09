import React, { useState, useContext } from 'react';
import styled from "styled-components";
import axios from 'axios';
import { Spin, Upload, message, Form, Input, Space, Button, Modal } from 'antd';
import { InboxOutlined } from '@ant-design/icons';
import { useNavigate } from 'react-router-dom';
import { FACE_API, LAUGHTER_API } from '../config';
import { LaughterContext } from '../context';
import { LoadingOutlined } from '@ant-design/icons';


const { Dragger } = Upload;


const getYoutubeVideoId = (url) => {
  var regExp = /^.*(youtu.be\/|v\/|u\/\w\/|embed\/|watch\?v=|\&v=)([^#\&\?]*).*/;
  var match = url.match(regExp);
  if (match && match[2].length == 11) {
    return match[2];
  } else {
    return false;
  }
};

function UploadVideo() {
  const [loading, setLoading] = useState(false);
  const [next, setNext] = useState(false);
  const [nextYT, setNextYT] = useState(false);
  const [video, setVideo] = useState('');
  const [res, setRes] = useState({});
  const [people, setPeople] = useState({});
  const [file, setFile] = useState();

  const { laughterTimeline, setLaughterTimeline } = useContext(LaughterContext);

  const navigate = useNavigate();

  const antIcon = <LoadingOutlined style={{ fontSize: 30, color: "#1B262C" }} spin />;

  const props = {
    name: 'file',
    multiple : false,
    beforeUpload: file  => {
      setFile(file)
    	return false;
    },
    file,
  }

  const handleClick = () => {
    res["video"] = video;
    res["people_img"] = people;
    navigate("/select-person", {
      state: res
    });
  };

  const handleYTClick = () => {
    res["people_img"] = people;
    navigate("/select-person", {
      state: res
    });
  };
  
  const onFinishFailed = () => {
    Modal.error({
      title: "입력한 URL이 잘못되었습니다.",
      content: "다시 URL을 확인해주세요.",
      centered: true,
      maskClosable: true,
    });
  };

  const uploadModule = () => {
    const upload_file = file
    if (!file) {
      Modal.error({
        title: "업로드한 파일이 없습니다.",
        content: "쇼츠를 추출할 영상을 업로드해주세요.",
        centered: true,
        maskClosable: true,
      });
      return ;
    }

    const url = window.URL.createObjectURL(upload_file);
    setVideo(url);

    const formData = new FormData();
    formData.append("file", upload_file);
    if (upload_file) {
      setLoading(true);
    }

    const getFaceClustering = () => {
      return axios({
        method: "post",
        url: `${FACE_API}/upload-video`, 
        data: formData,
        headers: {
          "Content-Type": "multipart/form-data",
        }
      });
    };

    const getLaughterDetection = () => {
      return axios({
        method: "post",
        url: `${LAUGHTER_API}/laughter-detection`,
        data: formData,
        headers: {
          "Content-Type": "multipart/form-data",
        }
      });
    };

    const getPeopleImg = async (res) => {
      return await axios.get(`${FACE_API}/show-people`, {params: {"id":  res}}
      ).then((response) => {
        setPeople(response.data.people_img)
        setLoading(false);
        setNext(true);
        message.success(`${file.name} 파일이 성공적으로 업로드되었습니다.`);
      }).catch((error) => {
        console.log('Failure :(');
        message.error(`${file.name} 파일을 업로드하는 데에 실패했습니다.`);
      });
    };

    getFaceClustering().then((response) => {
      setRes(response.data);
      getPeopleImg(response.data.id);
    }).catch((error) => {
      console.log("Failure :(");
    });

    getLaughterDetection().then((response) => {
      setLaughterTimeline(response.data.laugh);
    }).catch((error) => {
      console.log("Failure :(");
    });
  };

  const uploadYTModule = (url) => {
    if (!url["url"] || !getYoutubeVideoId(url["url"])) {
      onFinishFailed();
      return ;
    }
    setLoading(true);

    const getFaceClustering = () => {
      return axios({
        method: "post",
        url: `${FACE_API}/upload-video-youtube`, 
        data: url,
      });
    };

    const getLaughterDetection = () => {
      return axios({
        method: "post",
        url: `${LAUGHTER_API}/laughter-detection-youtube`,
        data: url,
      });
    };

    const getPeopleImg = async (res) => {
      return await axios.get(`${FACE_API}/show-people`, {params: {"id":  res}}
      ).then((response) => {
        setPeople(response.data.people_img)
        setLoading(false);
        setNextYT(true);
        message.success(`영상이 성공적으로 업로드되었습니다.`);
      }).catch((error) => {
        console.log('Failure :(');
        setLoading(false);
        message.error(`영상을 업로드하는 데에 실패했습니다. 다른 영상을 시도해보세요.`);
      });
    };

    getFaceClustering().then((response) => {
      setRes(response.data);
      getPeopleImg(response.data.id);
    }).catch((error) => {
      console.log("Failure :(");
      setLoading(false);
      message.error(error.response.data.message);
    });

    getLaughterDetection().then((response) => {
      setLaughterTimeline(response.data.laugh);
    }).catch((error) => {
      console.log("Failure :(");
    });
  };

  return (
    <div style={{padding: "20px"}}>
      <StyledIntro>
        <p style={{fontWeight: 'bold'}}>원하는 인물의 하이라이트 쇼츠를 생성하세요.</p>
        <p style={{color: '#444444'}}>예능 영상을 업로드하고</p>
        <p style={{color: '#777777'}}>인물을 선택하면 </p>
        <p style={{color: '#aaaaaa'}}>#눈#사람이 자동으로 쇼츠를 추출합니다.</p>
      </StyledIntro>
      <Spin indicator={antIcon} spinning={loading} size="large" tip="Extracting faces..." style={{fontSize:"15px", color: "#1B262C", fontWeight: "bold"}}>
        <div style={{width: "50%", margin: "0 auto", fontSize: "19px", textAlign: "left", fontWeight: "bold", marginBottom: "15px"}}>
          쇼츠 생성을 원하는 예능 영상 파일을 업로드해주세요.
        </div>
        <StyledUpload>
          <Dragger {...props} >
            <p className="ant-upload-drag-icon">
              <InboxOutlined />
            </p>
            <p style={{fontSize: '16px', color: '#000000', fontWeight: "bold"}}>클릭하거나 파일을 드래그하여 업로드</p>
            <p style={{fontSize: '14px', color: '#707070'}}>mp4 포맷을 지원합니다.</p>
          </Dragger>
        </StyledUpload>
        { next ? (
          <StyledButton onClick={handleClick} style={{backgroundColor: "#E5BD47"}}>인물 선택하기</StyledButton>
        ) : (
          <StyledButton onClick={uploadModule}>영상 업로드하기</StyledButton>
        ) }
        <StyledArea>
          <div style={{fontSize: "19px", textAlign: "left", fontWeight: "bold", marginBottom: "7px"}}>
            Youtube 영상은 URL을 이용하여 업로드할 수 있습니다.
          </div>
          <div style={{fontSize: "14px", textAlign: "left", marginBottom: "15px", color: '#707070'}}>
            720p를 지원하는 영상만 가능합니다.
          </div>
          <div style={{display: "flex"}}>
            <Form size={'large'} style={{flexGrow: "1", alignItems: "flex-start"}} autoComplete="off" onFinish={uploadYTModule} onFinishFailed={onFinishFailed} layout="inline">
              <Form.Item name="url" rules={[{ type: 'url', warningOnly: false }]} style={{flexGrow: "1", margin: "auto"}}>
                <Input placeholder="Youtube URL을 입력해주세요." />
              </Form.Item>
              <Space>
              { nextYT ? (
                <StyledYTButton onClick={handleYTClick} style={{backgroundColor: "#E5BD47", color: "white"}}>
                  인물 선택하기
                </StyledYTButton>
              ) : (
                <StyledYTButton htmlType="submit" style={{backgroundColor: "#1B262C", color: "white"}}>
                  Youtube 영상 업로드하기
                </StyledYTButton>
              ) }
              </Space>
            </Form>
          </div>
        </StyledArea>
      </Spin>
    </div>
  );
}

export default UploadVideo;

const StyledIntro = styled.div`
  margin: 0 auto;
  margin-top: 30px;
  margin-bottom: 50px;
  font-size: 20px;
  width: 50%;
  text-align: left;
`;

const StyledUpload = styled.div`
  background-color: #F7F7F7;
  margin: 0 auto;
  width: 50%;
`;

const StyledButton = styled.div`
  margin: 0 auto;
  margin-top: 30px;
  margin-bottom: 50px;
  width: 50%;
  padding: 10px;
  font-size: 17px;
  color: white;
  font-weight: bold;
  background-color: #1B262C;
  cursor : pointer;
  border-radius: 10px;
`;

const StyledArea = styled.div`
  width: 50%;
  margin: 0 auto;
  margin-bottom: 80px;
`;

const StyledYTButton = styled(Button)`
  margin-left: 30px;
  font-size: 17px;
  color: white;
  font-weight: bold;
  background-color: #000000;
  border-radius: 10px;
  outline: none !important;
  border: none !important;
  box-shadow: none !important; 
`;
