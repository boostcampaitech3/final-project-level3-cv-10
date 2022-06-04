import React, { useState, useEffect } from "react";
import axios from 'axios';
import { FACE_API } from '../config';

export default function Message() {

    const [result, setResult] = useState(null);
    const message = async () => {
        try {
            let res = await axios.get(`${FACE_API}/`);
            let result = res.data["message"];
            setResult(result);
        } catch(e) {
            console.log(e);
        }
    };

    useEffect(() => {
        message();
    }, []);

    return (
        <div>
            <h3>{result}</h3>
        </div>
    );
}
