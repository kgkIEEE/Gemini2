% Event response procedures for recommendation engine

% Events

classdef EventHandler
   properties
      timeOfEvent = 0.0;
      eventName = 'Nothing';
      eventMessage = 'Test';
   end
   methods
      function response = generateResponse(obj)
         response = 'No response';
         return;
      end
   end
end

