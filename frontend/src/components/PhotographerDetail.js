import React, { Component } from "react";

export default class PhotographerDetail extends Component {
  constructor(props) {
    super(props);
    this.state = {}
    this.slug = this.props.match.params.slug
    this.getPhotographer();
  }

  getPhotographer() {
    fetch('/api/photographer/'+this.slug)
      .then((response) => response.json())
      .then((data) => {
        this.setState(data);
      });
  }

  render() {
    return (<div>
        <div>
            <p>{this.state.name}</p>
            <p>{this.state.website}</p>
            <p>{this.state.instagram}</p>
            <p>{this.state.disk_space}</p>
        </div>
        <div>
          <a href="/">Go back</a>
        </div>
    </div>);
  }
}