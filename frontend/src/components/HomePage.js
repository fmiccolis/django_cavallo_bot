import React, { Component } from "react";

export default class HomePage extends Component {
  constructor(props) {
    super(props);
    this.state = {
      list: []
    };
    this.getAllPhotographers();
  }

  getAllPhotographers() {
    fetch('api/photographers')
      .then((response) => response.json())
      .then((data) => {
        this.setState({
          list: data
        });
      });
  }

  render() {
    return (
      <ul>
        {this.state.list.map((value, index) => {
          return <li id={value.id}>{value.name}</li>
        })}
      </ul>
    );
  }
}