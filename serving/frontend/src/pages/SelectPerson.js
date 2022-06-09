import { useLocation, useNavigate } from 'react-router-dom';
import { useEffect, useState, useRef } from 'react';
import styled from "styled-components";
import { PeoplePanel } from '../components';


function SelectPerson() {

    const location = useLocation();
    console.log(location.state);

    const ref = useRef();
    const [height, setHeight] = useState();
    const [loaded, setLoaded] = useState(false);

    const getVideoHeight = () => {
        if (ref.current) {
            setHeight(ref.current.clientHeight);
        }
    };
    useEffect(() => {
        getVideoHeight();
    }, [loaded]);

    useEffect(() => {
        window.addEventListener("resize", getVideoHeight);
    }, []);

    const navigate = useNavigate();
    useEffect(() => {
        if (!location.state) {
            navigate('/');
        }
    }, [location.state, navigate]);

    return (
        <div style={{padding: "20px"}}>
            <div style={{width: "75%", 
                margin: "0 auto", 
                marginBottom: "10px", 
                textAlign: "left", 
                fontWeight: "bold", 
                paddingTop: "30px",
                fontSize: "25px"}}>인물을 선택하세요.</div>
            { location.state !== null && (
                <StyledArea>
                    <div style={{flexGrow: "1", marginRight: "25px"}}>
                        <video ref={ref} width="100%" onLoadedData={() => {setLoaded(true)}} controls>
                            <source src={location.state.video} />
                        </video>
                    </div>
                    <div style={{flexGrow: "1"}}>
                        <PeoplePanel height={height} people={location.state.people_img} id={location.state.id} id_laughter={location.state.id_laughter} />
                    </div>
                </StyledArea>
            ) }
        </div>
    );
}

export default SelectPerson;

const StyledArea = styled.div`
    margin: 0 auto;
    margin-top: 40px;
    margin-bottom: 60px;
    width: 75%;
    align-items: flex-start;
    display: flex;
    justify-content: space-between;
`;
