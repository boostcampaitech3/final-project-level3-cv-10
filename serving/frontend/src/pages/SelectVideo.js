import React, { useState, useEffect } from 'react';
import styled from "styled-components";
import { Col, Row, Checkbox } from 'antd';
import { DownloadPanel } from '../components';
import { Video } from '../components';


// const STORAGE = "https://storage.googleapis.com/snowman-storage/";
const STORAGE = "https://storage.googleapis.com/snowman-bucket/";

const fake_response = {
    "id": "79b364b9-0f28-4d95-a2c5-23883e2cba2e",
    // video_url, duration(total length), score
    "shorts": [["person_00", "shorts_1.mp4", 20, 30],
                ["person_00", "shorts_6.mp4", 19, 20],
                ["person_01", "shorts_3.mp4", 32, 25],
                ["person_01", "shorts_4.mp4", 29, 34],
                ["person_02", "shorts_2.mp4", 29, 40],
                ["person_02", "shorts_5.mp4", 64, 39],],
    // might not be needed (or just list form)
    "people_img": {
        "person_00": "person_00.png",
        "person_01": "person_01.png",
        "person_02": "person_02.png",
        "person_03": "person_03.png",
        "person_04": "person_04.png",
    }
};


function SelectVideo() {
    
    const URL = STORAGE + fake_response.id;

    const [checkedList, setCheckedList] = useState([]);
    const [checkAll, setCheckAll] = useState(false);

    // 콘솔 확인용
    useEffect(() => {
        console.log(fake_response);
    }, []);

    const shorts_list = fake_response.shorts.map(function (element) {
        return element[1];
    });

    const renderCards = (shorts) => {
        const cards = [];
        // score 내림차순으로 정렬
        shorts.sort((a, b) => b[3] - a[3]);

        for (var i in shorts) {
            cards.push(
                <Col xxl={8} xl={8} lg={12} md={12} xs={24} key={i}>
                    <Video index={i} shorts={shorts} URL={URL} response={fake_response} />
                </Col>
            );
        };
        return cards;
    };
    
    const onChange = (list) => {
        setCheckedList(list);
        setCheckAll(list.length === fake_response.shorts.length);
    };

    const onCheckAllChange = () => {
        setCheckAll(!checkAll);
        setCheckedList(!checkAll ? shorts_list : []);
    };


    return (
        <div style={{padding: "20px"}}>
            <div style={{width: "85%", 
                margin: "0 auto", 
                marginBottom: "10px", 
                textAlign: "left", 
                fontWeight: "bold", 
                paddingTop: "30px",
                fontSize: "25px"}}
            >
                다운로드 할 쇼츠를 선택하세요.
            </div>
            <StyledArea>
                <div style={{width: "100%"}}>
                    <Checkbox.Group style={{width: "100%"}} value={checkedList} onChange={onChange}>
                        <Row gutter={16}>
                            {renderCards(fake_response.shorts)}
                        </Row>
                    </Checkbox.Group>
                </div>
                <DownloadPanel URL={URL} response={fake_response} checkedList={checkedList} 
                                checkAll={checkAll} onCheckAll={onCheckAllChange}/>
            </StyledArea>
        </div>
    );
};

export default SelectVideo;

const StyledArea = styled.div`
    margin: 0 auto;
    margin-top: 40px;
    width: 85%;
    align-items: flex-start;
    display: flex;
    justify-content: space-between;
`;
