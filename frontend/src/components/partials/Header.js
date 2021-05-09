import React, { Component } from "react";
import {AppBar, Button, IconButton, Toolbar, Typography} from "@material-ui/core";

export default class Header extends Component {
  constructor(props) {
    super(props);
    this.state = {
      mobileView: false,
      headersData: [
        {
          label: "Listings",
          href: "/listings",
        },
        {
          label: "Mentors",
          href: "/mentors",
        },
        {
          label: "My Account",
          href: "/account",
        },
        {
          label: "Log Out",
          href: "/logout",
        }
      ]
    }
    this.setResponsiveness = this.setResponsiveness.bind(this);
  }

  setResponsiveness() {
    return window.innerWidth < 900
      ? this.setState((prevState) => ({ ...prevState, mobileView: true }))
      : this.setState((prevState) => ({ ...prevState, mobileView: false }));
  };

  componentDidUpdate(prevProps, prevState, snapshot) {
    this.setResponsiveness();
    window.addEventListener("resize", () => this.setResponsiveness());
  }

  getMenuButtons() {
    return this.state.headersData.map(({ label, href }) => {
      return (
        <Button variant="outlined" href={href}>
          {label}
        </Button>
      );
    });
  }

  renderLogo() {
    return <Typography variant="h6" component="h1">
      Cavallo Production Bot
    </Typography>
  }

  displayDesktop() {
    return <Toolbar>
      {this.renderLogo()}
      {this.getMenuButtons()}
    </Toolbar>;
  };

  displayMobile() {
    return (
      <Toolbar>
        <IconButton
          {...{
            edge: "start",
            color: "inherit",
            "aria-label": "menu",
            "aria-haspopup": "true",
          }}
        >
          <MenuIcon />
        </IconButton>
        <div>{this.renderLogo()}</div>
      </Toolbar>
    );
  };

  render() {
    return <header><AppBar>{this.state.mobileView ? this.displayMobile() : this.displayDesktop()}</AppBar></header>;
  }
}