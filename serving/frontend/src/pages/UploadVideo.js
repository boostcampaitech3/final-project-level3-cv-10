import React, { useState } from 'react';
import styled from "styled-components";
import axios from 'axios';
import { Spin } from 'antd';
import { useNavigate } from 'react-router-dom';

const StyledIntro = styled.div`
  margin: 0 auto;
  margin-top: 50px;
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
  const [id, setId] = useState('');

  const navigate = useNavigate();

  const handleClick = () => {
    navigate("/select-person", {
      state: {
        id: id,
      },
    });
  }

  const uploadModule = async (e) => {
    e.preventDefault();
    const upload_file = e.target[0].files[0];

    const formData = new FormData();
    formData.append("file", upload_file);
    // formData.append("enctype", "multipart/form-data");
    if (upload_file) {
      setLoading(true);
    }

    const URL = "http://118.67.130.53:30001/upload-video";

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
      setId(response.data.id);
      console.log(response);
    }).catch((error) => {
      console.log('Failure :(');
    });
  }

  return (
    <>
      <StyledIntro>
        <p style={{fontWeight: 'bold'}}>원하는 인물의 하이라이트 쇼츠를 생성하세요.</p>
        <p style={{color: '#444444'}}>예능 영상을 업로드하고</p>
        <p style={{color: '#777777'}}>인물을 선택하면 </p>
        <p style={{color: '#aaaaaa'}}>#눈#사람이 자동으로 쇼츠를 추출합니다.</p>
      </StyledIntro>
      <Spin spinning={loading} size="large" tip="Loading...">
        <StyledUpload>
          <form onSubmit={uploadModule}>
            <p style={{fontSize: '18px', color: '#707070', fontWeight: 'bold'}}>원본 영상을 업로드해주세요.</p>
            <input type="file" accept="video/*" name="file" />
            <input type="submit" value="SUBMIT" />
          </form>
        </StyledUpload>
      </Spin>
      {
        next && (<StyledButton onClick={handleClick}>인물 추출 시작!</StyledButton>)
      }
    </>
  )
}

export default UploadVideo;