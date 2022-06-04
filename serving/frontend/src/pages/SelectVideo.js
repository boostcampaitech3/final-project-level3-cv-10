import React, { useState } from 'react';
import styled from "styled-components";
import { Col, Row, Checkbox } from 'antd';
import { DownloadPanel } from '../components';
import { Video } from '../components';
import { useLocation } from 'react-router-dom';
import { STORAGE } from '../config';


function SelectVideo() {

    const location = useLocation();
    console.log(location.state);

    const [checkedList, setCheckedList] = useState([]);
    const [checkAll, setCheckAll] = useState(false);

    const shorts_list = location.state.shorts.map(function (element) {
        return element[1];
    });

    const renderCards = (shorts) => {
        const cards = [];
        // score 내림차순으로 정렬
        shorts.sort((a, b) => b[3] - a[3]);

        for (var i in shorts) {
            cards.push(
                <Col xxl={8} xl={8} lg={12} md={12} xs={24} key={i} style={{display: "flex"}}>
                    <Video index={i} shorts={shorts} URL={STORAGE} response={location.state} />
                </Col>
            );
        };
        return cards;
    };
    
    const onChange = (list) => {
        setCheckedList(list);
        setCheckAll(list.length === location.state.shorts.length);
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
            { location.state !== {} && (
                <StyledArea>
                    <div style={{width: "100%"}}>
                        <Checkbox.Group style={{width: "100%"}} value={checkedList} onChange={onChange}>
                            <Row gutter={16}>
                                {renderCards(location.state.shorts)}
                            </Row>
                        </Checkbox.Group>
                    </div>
                    <DownloadPanel URL={STORAGE} response={location.state} checkedList={checkedList} 
                                    checkAll={checkAll} onCheckAll={onCheckAllChange}/>
                </StyledArea> 
            ) }
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
