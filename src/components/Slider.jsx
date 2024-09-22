/* eslint-disable no-unused-vars */

import React, { useState } from 'react'
import { ArrowBigLeft, ArrowBigRight } from 'lucide-react'

const Slider = ({images}) => {

    const [currentImage, setCurrentImage] = useState(0)
    // console.log(currentImage)
    return (
        <div className='slider-container'>
            <div className='slider'>
                {images.map((image, index) => (
                    <img key={index} className='slider-image' src={image} style={{translate: `${-100 * currentImage}%`}} alt="Frog" />
                ))}
            </div>
            <button className='slider-button' style={{left: '0'}} onClick={(() => setCurrentImage(prevCurrentImage => prevCurrentImage === 0 ? images.length - 1 : prevCurrentImage - 1))}>
                <ArrowBigLeft />
            </button>
            <button className='slider-button' style={{right: '0'}} onClick={(() => setCurrentImage(prevCurrentImage => prevCurrentImage < images.length - 1 ? prevCurrentImage + 1 : 0))}>
                <ArrowBigRight />
            </button>
            <div className='slider-dots-container'>
                {images.map((_, index) => (
                    index === currentImage ? (
                        <button key={index} className='slider-dot-active' onClick={() => setCurrentImage(index)}>
                            <span></span>
                        </button>
                    ) : (
                        <button key={index} className='slider-dot' onClick={() => setCurrentImage(index)}>
                            <span></span>
                        </button>
                    )
                ))}
            </div>
        </div>
    )
}

export default Slider