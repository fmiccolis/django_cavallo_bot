import React, {Component} from "react";
import {Col, Container, Row} from "react-bootstrap";
import PhotographerCard from "./partials/PhotographerCard"

export default class HomePage extends Component {
  constructor(props) {
    super(props);
    this.state = {
      list: [],
      fetch_finish: false
    };
    this.getAllPhotographers();
  }

  getAllPhotographers() {
    fetch('api/photographer/all')
    .then((response) => response.json())
    .then((data) => {
      this.setState({
        list: data,
        fetch_finish: true
      });
    });
  }

  componentDidMount() {
    document.title = this.props.title
  }

  render() {
    const items = []

    for (const [index, value] of this.state.list.entries()) {
      let events = []
      if(value.events.length > 0) {
        for (const event of value.events) {
          events.push(<li><a href={"/event/" + event.slug}>{event.name}</a></li>)
        }
      }
      let single =
          this.state.fetch_finish ?
              (<Col className="col-12 col-md-6 col-lg-4 mb-5 mb-lg-0">
                <a href={"/photographer/"+value.slug} style={{textDecoration: "none", color: "inherit"}}><PhotographerCard photographer={value} /></a>
                <ul>{events}</ul>
              </Col>) : (<h1>Loading</h1>)

      items.push(single)
    }

    return (
        <div className="section section-md mt-lg-5 mt-5 p-lg-5 p-2">
          <Container>
            <Row className="mb-5">
              {items}
            </Row>
          </Container>
        </div>)
  }
}