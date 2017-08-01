import React, { Component } from 'react';

import './InfoHeader.css';

export default class InfoHeader extends Component {
  render() {
    return (
      <div className='InfoHeader'>
        <h1>Salomondrin P-Nos Point Detector</h1>
        <p>
          This website shows the results
          of <a href='https://github.com/0xcaff'>0xcaff's</a> automatic P-Nos point
          collector, <a href='https://github.com/0xcaff/nos-stock'>nos-stock</a>.
          Check out the link to the project to find out how it works.

          Results are released 7 days after Salomondrin releases his video.
        </p>

        <p>
          <a href='https://github.com/0xcaff/nos-stock'>Fork Me On Github!</a>
        </p>
      </div>
    );
  }
}

