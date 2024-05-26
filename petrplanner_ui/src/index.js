import React, {useState, useEffect} from 'react';
import ReactDOM from 'react-dom/client';
import './index.css';
import App from './App';
import reportWebVitals from './reportWebVitals';

function Header() {
  return (
    <header>
      <h1>PetrPlanner</h1>
    </header>
  );
}

function Body({data}) {
  return (
    <div className="table-container">
      <table>
        <thead>
          <tr>
            <th>Course</th>
            <th>Section Code</th>
            <th>Section Type</th>
            <th>Section Number</th>
            <th>Units</th>
            <th>Instructors</th>
            <th>Meetings</th>
            <th>Max Capacity</th>
            <th>Currently Enrolled</th>
            <th>On Waitlist</th>
            <th>Status</th>
            <th>Score</th>
          </tr>
        </thead>
        <tbody>
          {Array.isArray(data) ? data.map((item, index) => (
            <tr key={index}>
              <td>{item.course}</td>
              <td>{item.sectionCode}</td>
              <td>{item.sectionType}</td>
              <td>{item.sectionNum}</td>
              <td>{item.units}</td>
              <td>{item.instructors.join(', ')}</td>
              <td>{item.meetings ? item.meetings.map(meeting => `${meeting.days} ${meeting.time}`).join(', ') : 'N/A'}</td>              <td>{item.maxCapacity}</td>
              <td>{item.numCurrentlyEnrolled ? item.numCurrentlyEnrolled.totalEnrolled : 'N/A'}</td>
              <td>{item.numOnWaitlist}</td>
              <td>{item.status}</td>
              <td>{item.score.toFixed(3)}</td>
            </tr>
          )) : null}
        </tbody>
      </table>
    </div>
  );
}

function GenerateButton({ onClick }) {
  return <button onClick={onClick}>Generate!</button>;
}

function Application() {
  const [showbody, setShowBody] = useState(false);
  const [loading, setLoading] = useState(false);
  const [data, setData] = useState({});

  const handleClick = async () => {
    setLoading(true);
    try {
      const response = await fetch('http://127.0.0.1:5001/api/data');
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      const data = await response.json();
      console.log('Data:', data[0]);
      setData(data);
      setShowBody(true);
    } catch (error) {
      console.error('There was a problem with the fetch operation:', error);
    } finally {

      setLoading(false);
      console.log('Loading:', loading);
    }
  };

  return (
    <React.StrictMode className="ReactStrictMode">
      <Header />
      <div className="button-container">
        {!showbody && (loading ? <p className="loading-message">Generating schedule...</p> : <GenerateButton key={loading.toString()} onClick={handleClick} />)}
      </div>
      {showbody && <Body data={data} />}
    </React.StrictMode>
  );
  
}


const root = ReactDOM.createRoot(document.getElementById('root'));
root.render(<Application />);

// If you want to start measuring performance in your app, pass a function
// to log results (for example: reportWebVitals(console.log))
// or send to an analytics endpoint. Learn more: https://bit.ly/CRA-vitals
reportWebVitals();
