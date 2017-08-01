import React, { Component } from 'react';
import { Link } from 'react-router-dom'
import InfoHeader from './InfoHeader';

import './VideoList.css';

export default class VideoList extends Component {
  render() {
    return (
      <div
        className='VideoList'>

        <InfoHeader />

        {this.props.videos.map(video =>
          <Link
            className='VideoItem'
            to={`/inferences/${video.id}`}
            key={video.id}>

            <div
              className='inner'>

              <div
                style={{ flex: '1' }}>

                <img
                  className='thumb'
                  alt='Thumbnail'
                  src={`//img.youtube.com/vi/${video.id}/0.jpg`} />
              </div>

              <div
                style={{
                  flex: '2',
                  marginLeft: '1em',
                }}>

                <h4>{ video.title }</h4>
              </div>
            </div>
          </Link>)}
      </div>
    );
  }
}

