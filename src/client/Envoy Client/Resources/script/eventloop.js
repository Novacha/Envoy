q.set_callback(function(item){
	var ui_scope = angular.element("[ng-controller=UiController]").scope()
	
	console.log(item);
	
	if(item.type == "roomlist_add")
	{
		$.each(item.data, function(i, element)
		{
			ui_scope.all_rooms.push(element)
		});
	}
	else if(item.type == "roomlist_remove")
	{
		var to_delete = [];
		
		$.each(item.data, function(i, element)
		{
			to_delete.push(element.jid);
		});
		
		ui_scope.all_rooms = ui_scope.all_rooms.filter(function(x, i, a){ return to_delete.indexOf(x.jid) === -1 });
	}
	else if(item.type == "joinlist_add")
	{
		$.each(item.data, function(i, element)
		{
			ui_scope.rooms.push(element)
		});
	}
	else if(item.type == "joinlist_remove")
	{
		var to_delete = [];
		
		$.each(item.data, function(i, element)
		{
			to_delete.push(element.jid);
		});
		
		ui_scope.rooms = ui_scope.rooms.filter(function(x, i, a){ return to_delete.indexOf(x.jid) === -1 });
	}
	else if(item.type == "user_status")
	{
		if(_.contains(ui_scope.users, item.data.jid))
		{
			ui_scope.users[item.data.jid].status = item.data.status;
		}
		else
		{
			ui_scope.users[item.data.jid] = {status: item.data.status};
		}
	}
	else if(item.type == "user_presence")
	{
		//var room_scope = angular.element("*[ng-controller=UiController] *[data]").scope()
	}
	
	ui_scope.$apply();
});

$(function(){
	setInterval(q.check, 150); /* FIXME: This is not very efficient. Surely, there's a better way to do this? */
});
