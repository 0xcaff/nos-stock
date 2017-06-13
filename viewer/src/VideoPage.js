import React, { Component } from 'react';
import './VideoPage.css';
import { getYT } from './YouTube';

// The frame rate of data which the inference was run on. Used to seek to the
// correct timestamp.
const FRAME_RATE = 30;

export default class Video extends Component {
  state = {
    inferences: [],
  };

  constructor(props) {
    super(props);

    this.getPlayer = this.getPlayer.bind(this);
    this.getInferences = this.getInferences.bind(this);
  }

  componentDidMount() {
    this.getInferences();
    this.getPlayer();
  }

  async getPlayer() {
    const YT = await getYT();
    this.player = new YT.Player('player');
  }

  async getInferences() {
    const resp = await fetch(
      `${process.env.PUBLIC_URL}/inferences/${this.props.id}.json`);

    const body = await resp.json();

    this.setState({inferences: body});
  }

  render() {
    return (
      <div className='video-page'>
        <iframe
          title='youtube'
          id="player"
          type="text/html"
          src={`https://www.youtube.com/embed/${this.props.id}?enablejsapi=1`}
          frameBorder="0" />

        <div>
          <h2>P-Nos Frames</h2>
          <ul>
            { this.state.inferences.map(inference => 
              <li
                key={inference.frame_number}>

                <span
                  style={{
                    cursor: 'pointer',
                    textDecoration: 'underline',
                  }}
                  onClick={(evt) => {
                    evt.preventDefault();
                    this.player.seekTo(inference.frame_number / FRAME_RATE);
                  }}
                  href="#">
                    Frame #{ inference.frame_number }
                </span>

                {` with score ${(inference.scores[0] * 100).toFixed(2)}`}
              </li>)}
          </ul>
        </div>
      </div>
    );
  }
}

