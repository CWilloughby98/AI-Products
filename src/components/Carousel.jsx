/* eslint-disable no-unused-vars */

import '../styles/carousel.css'
import React, { useState } from 'react'
import { ChevronLeft, ChevronRight } from 'lucide-react'

const Carousel = ({ products }) => {
	const [scrollPosition, setScrollPosition] = useState(0)

	const scroll = (direction) => {
		const wrapper = document.querySelector('.carousel-wrapper')
		const maxScroll = wrapper.scrollWidth - wrapper.clientWidth
		const newPosition = scrollPosition + direction * 300 // Adjust scroll amount as needed
		setScrollPosition(Math.max(0, Math.min(newPosition, maxScroll)))
	}

	return (
		<div className="carousel-container">
			<div className="carousel-wrapper" style={{ transform: `translateX(-${scrollPosition}px)` }}>
				{products.map((product, index) => (
					<div key={index} className="carousel-card">
						<img src={product.image}  />
						<div className="card-content">
							<h3>{product.title}</h3>
							<p>{product.description}</p>
							<span>{product.price + "€"}</span>
						</div>
					</div>
				))}
			</div>
			<button className="carousel-button prev" onClick={() => scroll(-1)}><ChevronLeft /></button>
			<button className="carousel-button next" onClick={() => scroll(1)}><ChevronRight /></button>
		</div>
	)
}

export default Carousel