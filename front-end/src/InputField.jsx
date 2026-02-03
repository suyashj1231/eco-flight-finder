import { useState } from 'react';
import './InputField.css';

function InputField() {

    const [departure, setDeparture] = useState('');
    const [arrival, setArrival] = useState('');
    const [date, setDate] = useState('');
    const [passengers, setPassengers] = useState(1);
    const [tripType, setTripType] = useState('One way');

    const handleSubmit = (event) => {
        event.preventDefault();
        console.log('Form submitted');
        console.log({ departure, arrival, date, passengers, tripType });
    };

    return (
        <form className="input-form" onSubmit={handleSubmit}>
            <div className='top-row'>
                <select value={tripType} onChange={(e) => setTripType(e.target.value)}>
                    <option value="One way">One Way</option>
                    <option value="Round trip">Round Trip</option>
                </select>

                <input type="number" placeholder="Passengers" min={1} value={passengers} onChange={(e) => setPassengers(parseInt(e.target.value))} />
            </div>
            <div className='bottom-row'>
                <input type="text" placeholder="Departing from?" value={departure} onChange={(e) => setDeparture(e.target.value)} />

                <input type="text" placeholder="Where to?" value={arrival} onChange={(e) => setArrival(e.target.value)} />

                <input type="date" value={date} onChange={(e) => setDate(e.target.value)} />

                <button type="submit" className="submit-button">✈️</button> {/* Flight emoji from ChatGPT */}
            </div>

        </form>
    );
}

export default InputField;