import React, { useState } from 'react';
import styled from "styled-components";
import axios from 'axios';
import { Spin } from 'antd';
import { useNavigate } from 'react-router-dom';
import { DownloadPanel } from '../components';
import ReactPlayer from 'react-player';

const fake_request = {
    "id": "79b364b9-0f28-4d95-a2c5-23883e2cba2e",
    // "file_name": "",
    // "created_at": "",
    // "final_timeline": {
    //     "person_00": [[20, 50, 1], [54, 80, 1]],
    //     "person_01": [[98, 134, 1]],
    //     "person_02": [[140, 179, 1]],
    //     "person_03": [[180, 210, 1]]
    // },
    "final_timeline": [[20, 50, 1], [54, 80, 1], [98, 134, 1], [140, 179, 1], [180, 210, 1]],
    "video": "https://storage.googleapis.com/snowman-storage/79b364b9-0f28-4d95-a2c5-23883e2cba2e/original.mp4",
    "people_img": {
        "person_00": "https://storage.googleapis.com/snowman-storage/79b364b9-0f28-4d95-a2c5-23883e2cba2e/person/person_00.png",
        "person_01": "https://storage.googleapis.com/snowman-storage/79b364b9-0f28-4d95-a2c5-23883e2cba2e/person/person_01.png",
        "person_02": "https://storage.googleapis.com/snowman-storage/79b364b9-0f28-4d95-a2c5-23883e2cba2e/person/person_02.png",
        "person_03": "https://storage.googleapis.com/snowman-storage/79b364b9-0f28-4d95-a2c5-23883e2cba2e/person/person_03.png"
    }
};

const StyledArea = styled.div`
    margin: 0 auto;
    margin-top: 40px;
    width: 80%;
    align-items: flex-start;
    display: flex;
    justify-content: space-between;
`;


function SelectVideo() {
    console.log(fake_request);

    return (
        <div style={{padding: "20px"}}>
            <div style={{width: "80%", 
                margin: "0 auto", 
                marginBottom: "10px", 
                textAlign: "left", 
                fontWeight: "bold", 
                paddingTop: "30px",
                fontSize: "25px"}}>저장할 쇼츠를 선택하세요.</div>
            <StyledArea>
                <div style={{backgroundColor: "lightblue", padding: "10px"}}>
                    <video width="60%" controls autoPlay>
                        <source src={fake_request.video + "#t=3.4,8"}></source>
                    </video>
                    {/* <ReactPlayer loop light playing url={fake_request.video + "#t=10,13"} /> */}
                    <ReactPlayer controls url={fake_request.video + "#t=10,13"} />
                </div>
                <DownloadPanel />
            </StyledArea>
        </div>
    );
}

export default SelectVideo;
