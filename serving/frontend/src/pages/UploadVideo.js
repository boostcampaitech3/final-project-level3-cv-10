import React, { useState } from 'react';
import styled from "styled-components";
import axios from 'axios';
import { Spin } from 'antd';
import { useNavigate } from 'react-router-dom';


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
  padding: 25px;
  border-radius: 10px;
  border: 2px dashed #E0E0E0;
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


function UploadVideo() {

  const [loading, setLoading] = useState(false);
  const [next, setNext] = useState(false);
  const [video, setVideo] = useState('');
  const [res, setRes] = useState({});

  const navigate = useNavigate();

  const handleClick = () => {
    res["video"] = video
    navigate("/select-person", {
      state: res
    });
  }

  const uploadModule = async (e) => {
    e.preventDefault();
    const upload_file = e.target[0].files[0];
    const url = window.URL.createObjectURL(upload_file);
    setVideo(url);

    const formData = new FormData();
    formData.append("file", upload_file);
    if (upload_file) {
      setLoading(true);
    }

    const URL = "http://101.101.218.23:30001/upload-video";

    await axios({
      method: "post",
      url: URL,
      data: formData,
      headers: {
        "Content-Type": "multipart/form-data",
      }
    }).then((response) => {
      setLoading(false);
      setNext(true);
      setRes(response.data)
      console.log(response);
    }).catch((error) => {
      console.log('Failure :(');
    });
  }

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
          <form onSubmit={uploadModule}>
            <p style={{fontSize: '18px', color: '#707070', fontWeight: 'bold'}}>원본 영상을 업로드해주세요.</p>
            <input type="file" accept="video/*" name="file" />
            <input type="submit" value="SUBMIT" />
          </form>
        </StyledUpload>
      </Spin>
      {
        next && (<StyledButton onClick={handleClick}>인물 선택하기!</StyledButton>)
      }
    </div>
  );
}

export default UploadVideo;
