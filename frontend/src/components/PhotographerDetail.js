import React, { Component } from "react";

export default class PhotographerDetail extends Component {
  constructor(props) {
    super(props);
    this.state = {
      photographer: "",
      finished_fetch: false
    }
    this.slug = this.props.match.params.slug
    this.getPhotographer();
  }

  componentDidMount() {
    document.title = this.props.match.params.slug
  }

  getPhotographer() {
    fetch('/api/photographer/'+this.slug)
      .then((response) => response.json())
      .then((data) => {
        this.setState({
          finished_fetch: true,
          photographer: data
        })
      });
  }

  render() {
    return (<div>
        <div>
          <a href="/">Go back</a>
        </div>
    </div>);
  }
}