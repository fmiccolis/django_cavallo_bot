import React, {Component} from "react";
import {
  BrowserRouter as Router,
  Switch,
  Route,
} from "react-router-dom";
import  "./../styles/main.scss";
import PhotographerDetail from "./PhotographerDetail";
import EventDetail from "./EventDetail";
import HomePage from "./HomePage";


export default class Dispatcher extends Component {
  constructor(props) {
    super(props);
  }

  render() {
    return (
      <Router>
        <Switch>
          <Route
              exact path="/"
              render={(props) => (
                  <HomePage {...props} title={"HomePage"} />
              )}
          />
          <Route exact path="/photographer/:slug" component={PhotographerDetail} />
          <Route exact path="/event/:slug" component={EventDetail} />
        </Switch>
      </Router>
    );
  }
}