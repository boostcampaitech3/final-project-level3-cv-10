import styled from "styled-components";
import { Avatar, Col, Image, Row, Modal } from 'antd';
import axios from 'axios';


const DownloadPanel = ({URL, response, checkedList, checkAll, onCheckAll}) => {

    // people_img는 이걸로 이용하면 ok!
    const people_img = [...new Set(response.shorts.map(short => short[0]))];
    console.log(people_img);

    const renderPeople = (URL, response) => {
        const people_imgs = [];
        for (var prop in people_img) {
            people_imgs.push(
                <Col xxl={8} xl={8} lg={8} md={8} sm={12} xs={24} key={prop}>
                    <div style={{margin: "3px", textAlign: "center"}} key={prop}>
                        <Avatar size={{xxl: 60, xl: 60, lg: 55, md: 50, sm: 50, xs: 50}} 
                            src={<Image src={URL + response.id + '/people/' + people_img[prop]} />} />
                    </div>
                </Col>
            );
        }
        return people_imgs;
    };

    const handleDownload = () => {
        if (checkedList.length) {
            checkedList.forEach((filename) => {
                axios({
                    url: URL + filename,
                    method: "GET",
                    // headers:
                    responseType: "blob"
                }).then(response => {
                    const url = window.URL.createObjectURL(new Blob([response.data]));
                    const link = document.createElement("a");
                    link.href = url;
                    link.setAttribute(
                        "download",
                        filename.split("/").pop()
                    );
                    document.body.appendChild(link);
                    link.click();
                    link.parentNode.removeChild(link);
                    window.URL.revokeObjectURL(url);
                });
            });
        } else {
            Modal.error({
                title: "선택한 영상이 없습니다.",
                content: "다운로드 할 쇼츠를 선택해주세요.",
                centered: true,
                maskClosable: true,
            });
        }
    };

    return (
        <StyledPanel>
            <div style={{textAlign: "left", fontSize: "17px", padding: "3px"}}>
                <div style={{marginBottom: "20px"}}>
                    <StyledTitle>
                        총 영상 개수
                    </StyledTitle>
                    <div style={{padding: "5px"}}>
                        {`${response.shorts.length}개`}
                    </div>
                </div>
                <div style={{marginBottom: "20px"}}>
                    <StyledTitle>
                        쇼츠 내 인물 정보
                    </StyledTitle>
                    <div style={{padding: "5px", marginTop: "5px", width:"100%", display: "flex"}}>
                        <Row gutter={5}>
                            {renderPeople(URL, response)}
                        </Row>
                    </div>
                </div>
            </div>
            <StyledButton onClick={onCheckAll}>
                {checkAll ? '전체 선택 해제' : '전체 선택'}
            </StyledButton>
            <StyledButton onClick={handleDownload}>선택한 영상 다운로드</StyledButton>
        </StyledPanel>
    );
};

export default DownloadPanel;

const StyledPanel = styled.div`
    width: 320px;
    padding: 10px;
    background-color: white;
    border-radius: 12px;
    border-style: dashed;
    border: 2px solid #0279C1;
    margin-left: 30px;
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

const StyledTitle = styled.span`
    font-weight: bold;
    border-radius: 5px;
    padding: 2px;
    background-color: #eeeeee;
`;
