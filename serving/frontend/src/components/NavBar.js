import styled from "styled-components";

const StyledNavBar = styled.nav`
  display: flex;
  background: #0279C1;
  width: 100%;
  height: 50px;
  color: white;
  justify-content: center;
  align-items: center;
  position: 'fixed';
`;

function NavBar() {
    return (
        <StyledNavBar>
            <span style={{fontSize: '20px', fontWeight: 'bold'}}>예능 하이라이트 <span style={{backgroundColor: 'white', color: '#0279C1', borderRadius: '2.5px'}}>#눈#사람</span> 에서 생성하세요!</span>
        </StyledNavBar>
    );
}

export default NavBar;
