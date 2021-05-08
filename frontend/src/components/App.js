import React, {Component} from 'react';
import  "./../styles/main.scss";
import Dispatcher from "./Dispatcher";


export default class App extends Component {
  constructor(props) {
    super(props);
  }

  render() {
    return (
      <div>
        <Dispatcher />
      </div>
    );
  }
}
