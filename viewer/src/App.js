import React, { Component } from 'react';
import VideoList from './VideoList';
import VideoPage from './VideoPage';
import { BrowserRouter as Router, Route } from 'react-router-dom';
import ffetch from './fetch';

import './App.css';

class App extends Component {
  state = {
    videos: [],
  };

  constructor(props) {
    super(props);

    this.getInferences = this.getInferences.bind(this);
  }

  componentDidMount() {
    this.getInferences();
  }

  getInferences() {
    const req = new Request(`${process.env.PUBLIC_URL}/inferences/index.json`);
    ffetch(req, async (resp) => this.setState({videos: await resp.json()}) );
  }

  render() {
    return (
      <Router
        basename={process.env.PUBLIC_URL}>

        <div>
          <Route
            exact path="/"
            render={() => <VideoList videos={this.state.videos} />} />

          <Route
            path="/inferences/:videoId"
            render={({ match }) => <VideoPage id={match.params.videoId} /> } />
        </div>
      </Router>
    );
  }
}

export default App;
