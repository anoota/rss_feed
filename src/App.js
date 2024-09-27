import React, { useEffect, useState } from 'react';
import './App.css';
import axios from 'axios';


function App() {
  const [articles, setArticles] = useState([]);
  const [language, setLanguage] = useState('eng');

  useEffect(() => {
    // Fetch articles from the backend
    axios.get('http://localhost:5000/get/rss')
      .then(response => {
        console.log('Response:', response);  // Print the full response object
        console.log('Data:', response.data); // Print only the data
        setArticles(response.data);          // Set the articles state
      })
      .catch(error => console.error('Error fetching articles:', error));
  }, []);

  const toggleLanguage = () => {
    setLanguage(language === 'eng' ? 'esp' : 'eng');
  };

  const today = new Date().toLocaleDateString('en-US', {
    weekday: 'short',    // "Mon"
    year: 'numeric',     // "2022"
    month: 'long',       // "August"
    day: 'numeric'       // "15"
  });


  return (
    <div className="App">
      <header className="sticky-header">
        <div className="date">{today}</div>
        <h1 className="nyt-header">{language === 'eng' ? 'The New York Times' : 'Los New York Times'}</h1>
        <button onClick={toggleLanguage}>{language === 'eng' ? 'ENG/ESP' : 'ESP/ENG'}</button>
      </header>
      <main>
      <ul className="article-list">
          {articles.map(article => (
            <li key={article.title} className="article-item">
              <div className="article-container">
                {article.image && <img src={article.image} alt={article.title} className="article-image" />}
                <div className="article-details">
                  <p className="article-date">{new Date(article.published).toLocaleDateString('en-US', {
                    weekday: 'short',
                    year: 'numeric',
                    month: 'long',
                    day: 'numeric'
                  })}</p>
                  <h2 className="article-title" onClick={() => window.open(article.link, '_blank')}>{article.title}</h2>
                  <p className="article-description">{article.description}</p>
                  <p className="article-byline">By {article.author || 'Unknown'}</p>
                </div>
              </div>
            </li>
          ))}
        </ul>
      </main>
    </div>
  );
}

export default App;
