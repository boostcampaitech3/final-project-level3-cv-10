import styled from "styled-components";

function Footer() {
    return (
        <StyledFooter>
            © 2022. <a style={{color: "#dddddd"}} href='https://github.com/boostcampaitech3/final-project-level3-cv-10'>#눈#사람</a>. All rights reserved.
        </StyledFooter>
    );
}

export default Footer;

const StyledFooter = styled.footer`
    background-color: #1B262C;
    color: #dddddd;
    padding: 30px 0;
    margin-top: auto;
`;
