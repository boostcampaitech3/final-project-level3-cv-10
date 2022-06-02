import { useLocation } from 'react-router-dom';
import { useEffect, useState } from 'react';
import axios from 'axios';
import styled from "styled-components";
import { PeoplePanel } from '../components';


const StyledArea = styled.div`
    margin: 0 auto;
    margin-top: 40px;
    width: 75%;
    align-items: flex-start;
    display: flex;
    justify-content: space-between;
`;


function SelectPerson() {
    const location = useLocation();
    console.log(location.state);

    const [people, setPeople] = useState({});
    const [filename, setFilename] = useState({});

    useEffect(() => {

        const getPeople = async () => {
            const URL = "http://101.101.218.23:30001/show-people";

            await axios.get(URL, {params: {"id":  location.state.id}}
            ).then((response) => {
                console.log(response);
                setPeople(response.data.people_img);
                setFilename(response.data.people_img_name);
            }).catch((error) => {
                console.log('Failure :(');
            });
        };
        getPeople();
    }, []);

    return (
        <div style={{padding: "20px"}}>
            <div style={{width: "75%", 
                margin: "0 auto", 
                marginBottom: "10px", 
                textAlign: "left", 
                fontWeight: "bold", 
                paddingTop: "30px",
                fontSize: "25px"}}>인물을 선택하세요.</div>
            <StyledArea>
                <video width="60%" controls>
                    <source src={location.state.video}></source>
                </video>
                <PeoplePanel people={people} id={location.state.id} id_laughter={location.state.id_laughter} filename = {filename}/>
            </StyledArea>
        </div>
    );
}

export default SelectPerson;
