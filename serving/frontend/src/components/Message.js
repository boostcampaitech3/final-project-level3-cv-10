import React, { useState, useEffect } from "react";
import axios from 'axios';

export default function Message() {

    const [result, setResult] = useState(null);
    const message = async () => {
        try {
            let res = await axios.get('http://118.67.130.53:30001/');
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
