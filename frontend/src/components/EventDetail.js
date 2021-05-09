import React, { Component } from "react";

export default class EventDetail extends Component {
  constructor(props) {
    super(props);
    this.state = {}
    this.slug = this.props.match.params.slug
    this.getPhotographer();
  }

  componentDidMount() {
    document.title = this.props.match.params.slug
  }

  getPhotographer() {
    fetch('/api/event/'+this.slug)
      .then((response) => response.json())
      .then((data) => {
        this.setState(data);
      });
  }

  render() {
    return (<div>
        <div>
            <p>{this.state.name}</p>
            <p>{this.state.photographer}</p>
            <p>{this.state.date}</p>
            <p><a href={this.state.url} target="_blank">{this.state.url}</a></p>
        </div>
        <div>
          <a href="/">Go back</a>
        </div>
    </div>);
  }
}