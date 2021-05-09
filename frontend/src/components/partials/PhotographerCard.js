import React, { Component } from "react";
import {Card, Col, Container, Image, Row} from "react-bootstrap";
import {FontAwesomeIcon} from "@fortawesome/react-fontawesome"
import {faGlobe} from "@fortawesome/free-solid-svg-icons"
import { faInstagram, faIntercom } from "@fortawesome/free-brands-svg-icons"
import {CardContent} from "@material-ui/core";

export default class PhotographerCard extends Component {
  constructor(props) {
      super(props);
      this.state = {}
  }

  componentDidMount() {
      this.setState(this.props.photographer);
  }

  render() {
    return (
      <Card className="shadow">
        <Image src="/static/images/profile-picture-1.jpg" />
        <CardContent>
          <h3 className="h5 card-title mt-3">{this.state.name}</h3>
          <p className="card-text">Some quick example text to build on the card title and
            make up the bulk of
            the card's content.</p>
          <span className="h6 icon-tertiary small">
            {this.state.instagram !== null ? (
                <a href={"https://www.instagram.com/"+this.state.instagram} target="_blank">
              <FontAwesomeIcon icon={faInstagram} className="me-2" size="lg" />
            </a>
            ) : null}
            {this.state.website !== null ? (
                <a href={this.state.website} target="_blank">
              <FontAwesomeIcon icon={faGlobe} className="me-2" size="lg" />
            </a>
            ) : null}
          </span>
        </CardContent>
      </Card>
    );
  }
}