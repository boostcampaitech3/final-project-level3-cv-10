import { useLocation } from 'react-router-dom';

function SelectPerson() {
    const location = useLocation();
    console.log(location.state);
    return (
        <div>
            <p>Face clustering 결과를 이용하여 사람을 선택합니다.</p>
            <p>서버에 업로드 된 영상 파일의 id는 "{location.state.id}"입니다.</p>
        </div>
    );
}

export default SelectPerson;
