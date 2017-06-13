import React, { Component } from 'react';
import VideoList from './VideoList';
import VideoPage from './VideoPage';
import { BrowserRouter as Router, Route } from 'react-router-dom';

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

  async getInferences() {
    const resp = await fetch(`${process.env.PUBLIC_URL}/inferences/index.json`);
    const body = await resp.json();

    this.setState({videos: body})
  }

  render() {
    return (
      <Router
        basename={process.env.PUBLIC_URL}>

        <div>
          <Route
            exact path="/"
            component={() => <VideoList videos={this.state.videos} />} />

          <Route
            path="/inferences/:videoId"
            component={(props) => <VideoPage id={props.match.params.videoId} />} />
        </div>
      </Router>
    );
  }
}

export default App;
