import { useState, useEffect, useRef } from 'react';
import './Autocomplete.css';

export default function Autocomplete({ name, value, onChange, placeholder, required = false }) {
    const [suggestions, setSuggestions] = useState([]);
    const [isOpen, setIsOpen] = useState(false);
    const [inputValue, setInputValue] = useState(value || '');
    const wrapperRef = useRef(null);

    // Sync internal state with prop
    useEffect(() => {
        setInputValue(value || '');
    }, [value]);

    useEffect(() => {
        function handleClickOutside(event) {
            if (wrapperRef.current && !wrapperRef.current.contains(event.target)) {
                setIsOpen(false);
            }
        }
        document.addEventListener("mousedown", handleClickOutside);
        return () => document.removeEventListener("mousedown", handleClickOutside);
    }, [wrapperRef]);

    const handleInput = async (e) => {
        const val = e.target.value;
        setInputValue(val);
        // Propagate changes to parent immediately
        onChange({ target: { name, value: val } });

        if (val.length < 2) {
            setSuggestions([]);
            setIsOpen(false);
            return;
        }

        try {
            const res = await fetch(`/airports/search?q=${encodeURIComponent(val)}`);
            if (res.ok) {
                const data = await res.json();
                setSuggestions(data);
                setIsOpen(true);
            }
        } catch (err) {
            console.error("Autocomplete fetch failed", err);
        }
    };

    const handleSelect = (airport) => {
        setInputValue(airport.iata);
        // Call parent with the IATA code
        onChange({ target: { name, value: airport.iata } });
        setSuggestions([]);
        setIsOpen(false);
    };

    return (
        <div className="autocomplete-wrapper" ref={wrapperRef}>
            <input
                type="text"
                name={name}
                value={inputValue}
                onChange={handleInput}
                placeholder={placeholder}
                required={required}
                autoComplete="off"
                className="autocomplete-input"
                style={{
                    /* Inline style to match InputField.css directly if class isn't enough */
                    width: '100%',
                    padding: '16px 20px',
                    fontSize: '1rem',
                    borderRadius: '12px',
                    border: '1px solid rgba(255, 255, 255, 0.4)',
                    background: 'rgba(255, 255, 255, 0.6)',
                    backdropFilter: 'blur(4px)',
                    color: 'var(--text-dark)',
                    fontFamily: 'var(--font-main)'
                }}
            />

            {isOpen && suggestions.length > 0 && (
                <ul className="suggestions-list">
                    {suggestions.map((s) => (
                        <li
                            key={s.iata}
                            className="suggestion-item"
                            onClick={() => handleSelect(s)}
                        >
                            <div className="airport-info">
                                <span className="airport-city">{s.city}, {s.country}</span>
                                <span className="airport-name">{s.name}</span>
                            </div>
                            <span className="airport-code">{s.iata}</span>
                        </li>
                    ))}
                </ul>
            )}
        </div>
    );
}
