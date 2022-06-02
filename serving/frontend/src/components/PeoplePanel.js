import { Radio, Spin } from 'antd';
import axios from 'axios';
import { useState } from 'react';
import styled from "styled-components";
import { useNavigate } from 'react-router-dom';


const StyledPanel = styled.div`
    width: 350px;
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
    margin: 5px;
    display: flex;
    align-items: center;
    font-size: 18px;
    font-weight: bold;
`;


function PeoplePanel(props) {
    const [value, setValue] = useState('');
    const [timeline, setTimeline] = useState();
    const [id, setId] = useState();
    const [res, setRes] = useState({});
    const navigate = useNavigate();

    const onChange = (e) => {
        console.log('Selected Person:', e.target.value);
        setValue(e.target.value);
      };

    const rendering = (people) => {
        console.log(props)
        const people_imgs = [];
        for (var prop in people) {
            people_imgs.push(
                <StyledPerson key={prop}>
                    <img src={`data:image/jpeg;base64,${people[prop]}`} 
                        width="80px"
                        style={{borderRadius: "35px"}} />
                    <div style={{flexGrow: "1"}}>
                        <div>{prop}</div>
                    </div>
                </StyledPerson>);
        }
        return people_imgs;
    };

    const handleClick = (tmp) => { navigate("/select-video", { state : tmp }); };


    const radioButton = (people) => {
        const buttons = [];

        for (var prop in people) {
            buttons.push(
                <Radio key={prop} value={prop} />
            );
        }

        return (
            <Radio.Group onChange={onChange} value={value} 
                style={{display: "flex", flexDirection: "column", justifyContent: "space-around"}}>
                {buttons}
            </Radio.Group>
        );
    };

    const personSelect = async(e) => {
        e.preventDefault();
        const URL = "http://101.101.218.23:30001/timeline-face";
        const FaceTimeline = () => {
            return axios({
                method:"post",
                url : "http://101.101.218.23:30001/timeline-face",
                data : {"face": [value], "id":props.id}
            })
        }
        const LaughTimeline = () => {
            return axios({
                method: "post",
                url : "http://118.67.130.53:30003/timeline-laughter",
                data : {"id" : props.id_laughter}
            })
        }
        await axios.all([FaceTimeline(), LaughTimeline()])
        .then(axios.spread(function (face_timeline, laugh_timeline) {
            var tmp = { ...face_timeline.data};
            tmp["laugh"] = laugh_timeline.data.laugh;
            setRes(tmp);
            console.log(res);
            handleClick(tmp);
        })).catch((error) => {
            console.log("Failure :(");
        });
        // await axios.post(URL, {"face":value, "id":props.id}
        // ).then((response)=> {
        //     console.log(response)
        //     setId(response.data.id)
        //     setTimeline(response.data.timeline)
        // }).catch((error) => {
        //     console.log("Failure :(")
        // })
    };

    return (
        <StyledPanel>
            <div style={{display: "flex", alignItems: "stretch"}}>
                <div style={{flexGrow: "1"}}>{rendering(props.people)}</div>
                <div style={{display: "flex", paddingRight: "10px", alignItems: "stretch"}}>
                    {radioButton(props.people)}
                </div>
            </div>
                <StyledButton onClick={personSelect}>
                        인물 선택 완료!
                </StyledButton>

            
        </StyledPanel>
    );
}

export default PeoplePanel;
