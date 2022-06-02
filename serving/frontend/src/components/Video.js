import React, { useState } from 'react';
import styled from "styled-components";
import { Avatar, Image, Checkbox, Modal } from 'antd';
import ReactPlayer from 'react-player';
import axios from 'axios';


const Video = ({index, shorts, URL, response}) => {
    const [hover, setHover] = useState(false);
    const [visible, setVisible] = useState(false);

    const getTime = (seconds) => {
        let min = parseInt((seconds % 3600)/60);
        let sec = seconds % 60;
        if (sec < 10)
            return `${min}:0${sec}`;
        return `${min}:${sec}`;
    };

    const downloadShorts = (filename) => {
        axios({
            url: URL + '/shorts/' + filename,
            method: "GET",
            // headers:
            responseType: "blob"
        }).then(response => {
            const url = window.URL.createObjectURL(new Blob([response.data]));
            const link = document.createElement("a");
            link.href = url;
            link.setAttribute(
                "download",
                filename
            );
            document.body.appendChild(link);
            link.click();
            link.parentNode.removeChild(link);
            window.URL.revokeObjectURL(url);
        });
    };

    return (
        <>
            <VideoItem>
                <div onMouseOver={() => setHover(true)} 
                    onMouseOut={() => setHover(false)} 
                    onClick={() => setVisible(true)}
                > 
                    {hover ? (
                        <ReactPlayer 
                            url={URL + '/shorts/' + shorts[index][1]}
                            muted={true}
                            width="100%"
                            height="auto"
                            playing={true}
                        />
                    ) : (
                        <ReactPlayer 
                            url={URL + '/shorts/' + shorts[index][1]}
                            muted={true}
                            width="100%"
                            height="auto"
                        />
                    )}
                </div>
                <VideoMeta>
                    <div>
                        <Avatar size={{xxl: 60, xl: 60, lg: 60, md: 50, sm: 50, xs: 50}} 
                                src={<Image src={URL + '/person/' + response.people_img[shorts[index][0]]} />} />
                    </div>
                    <div style={{paddingLeft: "15px", paddingRight: "10px", textAlign: "left",flexGrow: "1", justifyContent: "center", fontSize: "15px"}}
                        onClick={() => setVisible(true)}>
                        <div style={{fontWeight: "bold"}}>{shorts[index][1]}</div>
                        <div style={{color: "#555555"}}>{getTime(shorts[index][2])}</div>
                        <div style={{color: "#555555"}}>keywords</div>
                    </div>
                    <div>
                        <Checkbox value={shorts[index][1]}></Checkbox>
                    </div>
                </VideoMeta>
            </VideoItem>
            <Modal
                title={`${shorts[index][1]}`}
                centered
                visible={visible}
                cancelText="Close"
                onCancel={() => {setVisible(false)}}
                width={900}
                destroyOnClose={true}
                okText="Download"
                onOk={() => {downloadShorts(shorts[index][1])}}
            >
                <ReactPlayer 
                    url={URL + '/shorts/' + shorts[index][1]}
                    width="100%"
                    height="auto"
                    playing={true}
                    controls 
                />
            </Modal>
        </>
    );
};

export default Video;

const VideoItem = styled.div`
    border-radius: 10px;
    position: relative;
    margin-bottom: 10px;
    padding: 10px;
    word-break: break-all;
    overflow: auto;
    cursor : pointer;
    &:hover {
        background-color: #f1f1f1;
    }
`;

const VideoMeta = styled.div`
    padding: 3px;
    display: flex;
    align-items: center;
`;
