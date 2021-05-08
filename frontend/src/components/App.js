import React, {Component} from 'react';
import  "./../styles/main.scss";
import Dispatcher from "./Dispatcher";
import Header from "./partials/Header";
import Footer from "./partials/Footer";


export default class App extends Component {
  constructor(props) {
    super(props);
  }

  render() {
    return (
      <div>
        <Header />
        <Dispatcher />
        <Footer />
      </div>
    );
  }
}
