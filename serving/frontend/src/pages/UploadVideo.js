import React, { useState } from 'react';
import styled from "styled-components";
import axios from 'axios';
import { Spin, Upload, message } from 'antd';
import { InboxOutlined } from '@ant-design/icons';
import { useNavigate } from 'react-router-dom';
import { FACE_API, LAUGHTER_API } from '../config';


const { Dragger } = Upload;

function UploadVideo() {
  const [loading, setLoading] = useState(false);
  const [next, setNext] = useState(false);
  const [video, setVideo] = useState('');
  const [res, setRes] = useState({});
  const [people, setPeople] = useState({});
  const [file, setFile] = useState();

  const navigate = useNavigate();

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
    res["video"] = video
    res["people_img"] = people
    navigate("/select-person", {
      state: res
    });
  };

  const uploadModule = async () => {
    const upload_file = file
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
        url: `${LAUGHTER_API}/upload-video`,
        data: formData,
        headers: {
          "Content-Type": "multipart/form-data",
        }
      });
    };

    const getPeopleImg = (res) => {
      return axios.get(`${FACE_API}/show-people`, {params: {"id":  res}}
      ).then((response) => {
        console.log(response);
        setPeople(response.data.people_img)
        setLoading(false);
        setNext(true);
        message.success(`${file.name} file uploaded successfully.`);
      }).catch((error) => {
        console.log('Failure :(');
        message.error(`${file.name} file upload failed.`);
      });
    }

    await axios.all([getFaceClustering(), getLaughterDetection()])
      .then(axios.spread(function (face_clustering, laughter_detection) {
          var tmp = { ...face_clustering.data};
          tmp["id_laughter"] = laughter_detection.data.id_laughter;
          setRes(tmp);
          console.log(tmp);
          getPeopleImg(tmp["id"])
      })).catch((error) => {
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
      <Spin spinning={loading} size="large" tip="Extracting faces...">
        <StyledUpload>
          <Dragger {...props} >
            <p className="ant-upload-drag-icon">
              <InboxOutlined />
            </p>
            <p style={{fontSize: '18px', color: '#707070', fontWeight: 'bold'}}>원본 영상을 업로드해주세요.</p>
          </Dragger>
        </StyledUpload>
      </Spin>
      {
        !next && (<StyledButton onClick={uploadModule}>비디오 업로드하기!</StyledButton>)
      }
      {
        next && (<StyledButton onClick={handleClick}>인물 선택하기!</StyledButton>)
      }
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
  margin-top: 50px;
  width: 50%;
  padding: 10px;
  font-size: 18px;
  color: white;
  font-weight: bold;
  background-color: #000000;
  cursor : pointer;
  border-radius: 10px;
`;
