import { useState, lazy, Suspense } from 'react'
import slide1 from "./assets/slide1.png"
import slide2 from "./assets/slide2.jpeg"
import slide3 from "./assets/slide3.jpeg"
import Slider from './components/Slider'
import SearchBar from './components/SearchBar'
import './styles/App.css'

const Carousel = lazy(() => import('./components/Carousel'))

function App() {
  const [products, setProducts] = useState([])
  const [isLoading, setIsLoading] = useState(false)
  const images = [slide1, slide2, slide3]
  const [showPopup, setShowPopup] = useState(false);

  const fetchProducts = async (searchTerm = '') => {
    setIsLoading(true);
    setShowPopup(false);
    try {
      console.log("fetching products...");
      const response = await fetch(`http://localhost:5000/api/search?search_query=${encodeURIComponent(searchTerm)}`);
      if (!response.ok) {
        throw new Error('Network response was not ok');
      }
      const data = await response.json();
      setProducts(data);
      if (data.length === 0) {
        setShowPopup(true);
      }
    } catch (error) {
      console.error("Could not fetch products:", error);
      setShowPopup(true);
    } finally {
      setIsLoading(false);
    }
  }

  const handleSearch = (searchTerm) => {
    fetchProducts(searchTerm);
  }

  console.log(products)
  console.log(isLoading)
  return (
    <Suspense fallback={<div>Loading components...</div>}>
      <div className='mb-5'>
        <Slider images={images} />
      </div>
      <SearchBar onSearch={handleSearch} />
      {isLoading ? (
        <div className="spinner-container">
          <div className="spinner"></div>
        </div>
      ) : (
        products.length > 0 && (
          <div>
            <Carousel products={products} />
          </div>
        )
      )}
      {showPopup && (
        <div className="popup">
          <p>No products found. Please try using a broader search term.</p>
          <button onClick={() => setShowPopup(false)}>Close</button>
        </div>
      )}
    </Suspense>
  )
}

export default App
