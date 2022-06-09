import styled from "styled-components";
import { Link } from 'react-router-dom';


function Header() {

    return (
        <StyledHeader>
            <Link to="/" style={{color: "white", fontSize: '20px', fontWeight: 'bold'}}>
                인물 기반 예능 쇼츠 <span style={{padding: "0.5px", backgroundColor: 'white', color: '#0279C1', borderRadius: '2.5px'}}>#눈#사람</span> 에서 생성하세요!
            </Link>
        </StyledHeader>
    );
}

export default Header;

const StyledHeader = styled.nav`
  display: flex;
  background: #0279C1;
  width: 100%;
  height: 50px;
  justify-content: center;
  align-items: center;
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  z-index: 1;
`;
