import React, { useState, useEffect } from "react";
import "./App.css";
import { Backdrop, CircularProgress } from "@mui/material";

function App() {
  const [query, setQuery] = useState("");
  const [images, setImages] = useState([]);
  const [videos, setVideos] = useState([]);
  const [error, setError] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [retryImageCount, setRetryImageCount] = useState(0);
  const [retryVideoCount, setRetryVideoCount] = useState(0);

  const fetchImages = async () => {
    if (!query.trim()) return;

    setError(null);
    setIsLoading(true);

    try {
      const response = await fetch(`http://backend:6743/image-search`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ query }),
      });

      const imageData = await response.json();
      const fetchedImages = imageData?.images.map((item) => ({
        imgSrc: item.img_src,
        url: item.url,
        title: item.title,
      }));

      setImages(fetchedImages);
      setIsLoading(false);
    } catch (err) {
      console.error(err);
      setError("Failed to fetch images. Please try again.");
      setIsLoading(false);
    }
  };

  const fetchVideos = async () => {
    if (!query.trim()) return;

    setError(null);
    setIsLoading(true);

    try {
      const response = await fetch(`http://backend:6743/video-search`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ query }),
      });

      const videoData = await response.json();
      const fetchedVideos = videoData.videos.slice(0, 20);

      setVideos(fetchedVideos);
      setIsLoading(false);
    } catch (err) {
      console.error(err);
      setError("Failed to fetch videos. Please try again.");
      setIsLoading(false);
    }
  };

  const handleSearch = () => {
    fetchImages();
    fetchVideos();
  };

  useEffect(() => {
    if (images.length === 0 && retryImageCount < 3) {
      const timer = setTimeout(() => {
        setRetryImageCount(retryImageCount + 1);
        fetchImages();
      }, 2000);

      return () => clearTimeout(timer);
    }
  }, [images, retryImageCount]);

  useEffect(() => {
    if (videos.length === 0 && retryVideoCount < 3) {
      const timer = setTimeout(() => {
        setRetryVideoCount(retryVideoCount + 1);
        fetchVideos();
      }, 2000);

      return () => clearTimeout(timer);
    }
  }, [videos, retryVideoCount]);

  return (
    <div className='App'>
      <div className='search-container'>
        <textarea
          type='text'
          placeholder='Enter search query...'
          value={query}
          onChange={(e) => setQuery(e.target.value)}
        />
        <button onClick={handleSearch} disabled={isLoading}>
          {isLoading ? "Loading..." : "Send"}
        </button>
      </div>
      {error && <p className='error'>{error}</p>}

      <div className='results'>
        <h2>Images</h2>
        <div className='images'>
          {images.length > 0 ? (
            images.map((image, index) => (
              <div key={index} className='image-item'>
                <img src={image.imgSrc} alt={`Result ${index + 1}`} />
              </div>
            ))
          ) : (
            <p>No images found.</p>
          )}
        </div>

        <h2>Videos</h2>
        <div className='images'>
          {videos.length > 0 ? (
            videos.map((video, index) => (
              <div key={index}>
                <iframe
                  src={video.iframe_src}
                  title={video.title}
                  width='560'
                  height='315'
                  frameBorder='0'
                  allow='accelerometer; encrypted-media; gyroscope; picture-in-picture'
                  allowFullScreen
                ></iframe>
              </div>
            ))
          ) : (
            <p>No videos found.</p>
          )}
        </div>
      </div>

      <Backdrop
        sx={{
          color: "#fff",
          zIndex: (theme) => theme.zIndex.drawer + 1,
        }}
        open={isLoading}
      >
        <CircularProgress color='inherit' />
      </Backdrop>
    </div>
  );
}

export default App;
