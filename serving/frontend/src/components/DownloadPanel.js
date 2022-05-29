import { useState } from 'react';
import styled from "styled-components";

const StyledPanel = styled.div`
    width: 300px;
    padding: 10px;
    background-color: white;
    border-radius: 12px;
    border-style: dashed;
    border: 2px solid #0279C1;
    margin-left: 20px;
`;

const StyledButton = styled.div`
    margin: 0 auto;
    margin-top: 10px;
    padding: 10px;
    font-size: 18px;
    color: white;
    font-weight: bold;
    background-color: #000000;
    cursor : pointer;
    border-radius: 10px;
`;


function DownloadPanel() {
    return (
        <StyledPanel>
            <div style={{display: "flex", alignItems: "stretch"}}>
            </div>
            <StyledButton>선택한 영상 다운로드</StyledButton>
        </StyledPanel>
    );
}

export default DownloadPanel;
