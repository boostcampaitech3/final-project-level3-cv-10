import { Spin, Checkbox, Avatar, Image } from 'antd';
import axios from 'axios';
import { useState } from 'react';
import styled from "styled-components";
import { useNavigate } from 'react-router-dom';

const STORAGE = "https://storage.googleapis.com/snowman-bucket/";

function PeoplePanel(props) {

    const [checkedList, setCheckedList] = useState([]);
    const [loading, setLoading] = useState(false);
    const navigate = useNavigate();

    const handleClick = (res) => { 
        
        navigate("/select-video", { state : res }); 
    };

    const onChange = (list) => {
        setCheckedList(list);
        console.log(list);
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
            "http://101.101.218.23:30001/timeline-highlight", res // 101.101.218.23
        ).then((response) => {
            console.log(response);
            setLoading(false);
            handleClick(response.data);
        });
    };

    const personSelect = async () => {
        // e.preventDefault();
        setLoading(true);

        const FaceTimeline = () => {
            return axios({
                method:"post",
                url : "http://101.101.218.23:30001/timeline-face", // 101.101.218.23
                data : {"face": checkedList, "id":props.id}
            });
        };

        const LaughTimeline = () => {
            return axios({
                method: "post",
                url : "http://118.67.130.53:30003/timeline-laughter",
                data : {"id" : props.id_laughter}
            });
        };

        console.log('checkedList', checkedList);
        
        await axios.all([FaceTimeline(), LaughTimeline()])
        .then(axios.spread(function (face_timeline, laugh_timeline) {
            var res = { ...face_timeline.data};
            res["laugh"] = laugh_timeline.data.laugh;
            res["people_img"] = props.people
            getHighlight(res);
            console.log(res);
        })).catch((error) => {
            console.log("Failure :(");
        });
    };

    return (
        <StyledPanel>
            <Spin spinning={loading} size="large" tip="Making shorts...">
            <div>
                <Checkbox.Group style={{width: "100%"}} value={checkedList} onChange={onChange}>
                    {render(props.people)}
                </Checkbox.Group>
            </div>
            <StyledButton onClick={personSelect}>
                    인물 선택 완료!
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
    background-color: #000000;
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
