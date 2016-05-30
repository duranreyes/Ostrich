import React from 'react';
import { Modal } from 'react-bootstrap';

const AppModal = React.createClass({
    
    render() {
        return (
            <Modal show={this.props.show} onHide={this.props.hide} bsSize="sm">
                <Modal.Header closeButton>
                    <Modal.Title>{this.props.title}</Modal.Title>
                </Modal.Header>
                <Modal.Body>
                   
                    <div>Download app from Android Store to</div>
                    <ul>
                        <li>
                            <span className="glyphicon glyphicon-star gold" aria-hidden="true"></span> Order any book in a few taps
                        </li>
                        <li>
                            <span className="glyphicon glyphicon-star gold" aria-hidden="true"></span> Keep track of your orders and extend them
                        </li>
                        <li>
                            <span className="glyphicon glyphicon-star gold" aria-hidden="true"></span>  Share with your friends
                        </li>
                    </ul> 
                    <div className="install-container clearfix">
                        <a target="_blank" href='https://play.google.com/store/apps/details?id=in.hasslefree.ostrichbooks&hl=en&utm_source=global_co&utm_medium=prtnr&utm_content=Mar2515&utm_campaign=PartBadge&pcampaignid=MKT-Other-global-all-co-prtnr-py-PartBadge-Mar2515-1'><img id="play-store" alt='Get it on Google Play' src='https://play.google.com/intl/en_us/badges/images/generic/en_badge_web_generic.png'/></a>
                    </div>
                </Modal.Body>
            </Modal>
        );
    }
});

export default AppModal;
