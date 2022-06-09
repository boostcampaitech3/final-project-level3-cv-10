import { Spin, Checkbox, Avatar, Image, Modal } from 'antd';
import axios from 'axios';
import { useState, useContext, useEffect } from 'react';
import styled from "styled-components";
import { useNavigate } from 'react-router-dom';
import { STORAGE, FACE_API } from '../config';
import { LaughterContext } from '../context';
import { LoadingOutlined } from '@ant-design/icons';


function PeoplePanel(props) {

    const [checkedList, setCheckedList] = useState([]);
    const [loading, setLoading] = useState(false);
    const navigate = useNavigate();

    const { laughterTimeline, setLaughterTimeline } = useContext(LaughterContext);
    const [faceResult, setFaceResult] = useState(null);

    const antIcon = <LoadingOutlined style={{ fontSize: 30, color: "#1B262C" }} spin />;
    
    useEffect(() => {
        // laughterTimeline과 faceResult(faceTimeline)가 모두 추출된 경우
        if (laughterTimeline && faceResult) {
            var res = {...faceResult};
            res["laugh"] = laughterTimeline;
            getHighlight(res);
        }
    }, [laughterTimeline, faceResult]);

    const handleClick = (res) => { 
        navigate("/select-video", { state : res }); 
    };

    const onChange = (list) => {
        setCheckedList(list);
    };

    const render = (people) => {
        const person = [];
        for (var prop in people) {
            person.push(
                <StyledPerson key={prop}>
                    <div>
                        <Avatar size={80} src={<Image src={STORAGE + people[prop]} />}  />
                    </div>
                    <div style={{paddingLeft: "10px", paddingRight: "10px", textAlign: "center",flexGrow: "1", justifyContent: "center", fontSize: "15px"}}>
                        <div>{prop}</div>
                    </div>
                    <div>
                        <Checkbox value={prop}></Checkbox>
                    </div>
                </StyledPerson>
            );
        }
        return person;
    };

    const getHighlight = async(res) => {
        await axios.post(
            `${FACE_API}/timeline-highlight`, res
        ).then((response) => {
            setLoading(false);
            handleClick(response.data);
        });
    };

    const personSelect = async() => {
        const FaceTimeline = () => {
            return axios({
                method:"post",
                url : `${FACE_API}/timeline-face`, 
                data : {"face": checkedList, "id":props.id}
            });
        };

        if (checkedList.length) {
            setLoading(true);
            await FaceTimeline().then((response) => {
                var res = {...response.data};
                res["people_img"] = props.people;
                setFaceResult(res);
            }).catch((error) => {
                console.log("Failure :(");
            });
        } else {
            Modal.error({
                title: "선택한 인물이 없습니다.",
                content: "쇼츠를 추출할 인물을 선택해주세요.",
                centered: true,
                maskClosable: true,
            });
        }
    }

    return (
        <StyledPanel>
            <Spin indicator={antIcon}
                spinning={loading} 
                style={{position: "absolute", top: "50%", transform: "translateY(-50%)", fontSize:"15px", color: "#1B262C", fontWeight: "bold"}} 
                size="large" 
                tip="Making shorts...">
                <div style={{maxHeight: props.height, overflow: "auto"}}>
                    <Checkbox.Group style={{width: "100%"}} value={checkedList} onChange={onChange}>
                        {render(props.people)}
                    </Checkbox.Group>
                </div>
                <StyledButton onClick={personSelect}>
                    인물 선택 완료
                </StyledButton>
            </Spin>
        </StyledPanel>
    );
}

export default PeoplePanel;

const StyledPanel = styled.div`
    width: 280px;
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
    background-color: #1B262C;
    cursor : pointer;
    border-radius: 10px;
`;

const StyledPerson = styled.div`
    padding: 10px;
    display: flex;
    align-items: center;
    font-size: 18px;
    font-weight: bold;
    border-radius: 10px;
    &:hover {
        background-color: #f1f1f1;
    }
`;
