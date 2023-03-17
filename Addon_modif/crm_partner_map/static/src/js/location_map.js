
function map_loaded() {}

var location_map_widget;

openerp.crm_partner_map = function (instance)
{   

	instance.web.form.widgets.add('location_map', 'instance.crm_partner_map.Map');

	instance.crm_partner_map.Map = instance.web.form.AbstractField.extend({
		id: null, // partner's id
		map: null, // google.maps.Map instance
		marker: null, // partner's location marker
		template: 'location_map',

		set_value: function(value) {
			this.id = value;			
			if(this.map != null & value != false) {
				var Partner = new instance.web.Model('res.partner');
				Partner.query(['partner_latitude', 'partner_longitude'])
					.filter([['id', '=', this.id]]).limit(1)
					.all().done(
						$.proxy(
						function(partner) {
							// create marker
							var lat = partner[0].partner_latitude;
							var lng = partner[0].partner_longitude;
							if(this.map) {
								if(this.marker != null) {
									this.marker.setMap(null);
									delete this.marker;									
								}
								this.map.panTo(new google.maps.LatLng(lat, lng));
								this.map.setZoom(16);									
								if(lat != 0.0 & lng != 0.0) {
									this.marker = new google.maps.Marker({
										position : new google.maps.LatLng(lat, lng),
										map : this.map,
										draggable : false,
										raiseOnDrag : true});
								}
								
							}
						
						}, this)
					
					);
												
			}
			
		},
		init: function(parent, options) {
			location_map_widget = this; // needed for workaround below
			// load google's api
			if(typeof(google) == "undefined") {
				$.getScript("http://maps.googleapis.com/maps/api/js?sensor=false&callback=map_loaded");						
			}			
			this._super(parent, options);
		},
		
		start: function () {
			// initialize the widget with new map
				if(typeof(google) != "undefined") { // clear offline usage errors....
					    this.map = new google.maps.Map(document.getElementById("location_map"), 
										{zoom: 2, center: new google.maps.LatLng(0.0, 0.0), mapTypeId: google.maps.MapTypeId.ROADMAP});				

					// its an ugly workaround with JQuery's tab issue...					
						$('.ui-tabs').each(function() {
							$(this).bind('tabsshow', function(event, ui) {
									if(ui.tab.innerText == "Geo Localization") {
								        google.maps.event.trigger(location_map_widget.map, 'resize');
										if(location_map_widget.marker != null) {
											location_map_widget.map.panTo(location_map_widget.marker.getPosition());
										}
									}
							    });
						});
				} else {
					this.$el.text("Couldn't load Goole Map API. Please check internet connection and reload the page.");
				}
			
			// have to refresh the value
			this.set_value(this.id);
			return this._super();
		},

	});

}

