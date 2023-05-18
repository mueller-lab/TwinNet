import math


class ObjectTracker:
    def __init__(self):
        self.title = 'ObjectTracker'
        self.distanceThreshold = 100
        self.prediction_IDs_display_current = []
        self.prediction_IDs_deregistered = {}
        self.prediction_IDs_overall_used = []
        self.prediction_ID_next_usable = 0
        self.prediction_slides_deregistered_threshold = 10

    def object_tracking_initialize(self, predictions_old):
        """
        This method uses the first set of predicted embryos to
        update following initial parameters and variables:
            
            self.prediction_IDs_display_current
            self.prediction_IDs_deregistered
            self.prediction_IDs_overall_used
            
        Args:
            predictions_old = {x: [prediction_score, prediction_class,
                                   [ymin, xmin, ymax, xmax]] }
        """
        
        for x in predictions_old:
            self.prediction_IDs_display_current.append(x)
            self.prediction_IDs_overall_used.append(x)
            self.prediction_IDs_deregistered[x] = 0
        
        self.prediction_ID_next_usable = int(max(predictions_old.keys())) + 1
        
    @staticmethod
    def predictions_to_centroids_convert(predictions):
        """
        This method converts the models sorted boxes to centroids.
        
        Args:
            predictions = {x: [prediction_score, prediction_class,
                               [ymin, xmin, ymax, xmax]] }
        
        Returns:
            centroids = {x: [centerx, centery]}
        
        """
        centroids = {}
        
        for x in predictions:
            bboxes = predictions[x][2]
            
            xmin = bboxes[1]
            ymin = bboxes[0]
            xmax = bboxes[3]
            ymax = bboxes[2]
            
            centerx = int(xmin + ((xmax - xmin) / 2))
            centery = int(ymin + ((ymax - ymin) / 2))
            
            centroid = [centerx, centery]
        
            centroids[x] = centroid
        
        return centroids

    @staticmethod
    def predictions_number_get(predictions):
        """
        This method returns the number of predictions.
        
        Args:
            predictions = {x: [prediction_score, prediction_class,
                               [ymin, xmin, ymax, xmax]] }
        
        Returns:
            scalar value X (number_of_predictions, equal to the length of
            the dictionary predictions)
            
        """
        return len(predictions.keys())

    @staticmethod
    def distance_two_centroids_calculate(centroid_old, centroid_new):
        """
        This method calculates the distance between two points/centroids,
        that are defined by x and y value.
        
        Args:
            centroid_old = [X1, Y1]
            centroid_new = [X2, Y2]

        Returns:
            scalar value X (distance)
        """
        x1, y1 = centroid_old
        x2, y2 = centroid_new        
        
        distance = math.hypot(x2 - x1, y2 - y1)

        return distance

    def distances_dict_from_old_centroids_and_new_centroids_calculate(
            self, centroids_old, centroids_new):
        """
        This method utilizes the previous method
        'distance_two_centroids_calculate' to calculate
        the distances between two dictionaries of variable length,
        i.e. variable numbers of centroids.
        
        Parameters
        ----------
            centroids_old = {o0: [X0, Y0], o1: [X1, Y1], ..., on: [Xn, Yn]}
            centroids_new = {n0: [X0, Y0], n1: [X1, Y1], ..., nn: [Xn, Yn]}

        Returns
        -------
            distances_centroids_old_centroids_new = {
                o0: [d n0, d n1, ..., d nn],
                o1: [d n0, d n1, ..., d nn],
                ...: [d n0, d n1, ..., d nn],
                on: [d n0, d n1, ..., d nn]
            }

        Raises
        ------
        None.
        """
        distances_centroids_old_centroids_new = {}
        
        for i in centroids_old:
            # centroid old get [Xn, Yn]
            centroid_old_instance = centroids_old[i]
            
            centroid_old_instance_distances = []
            
            for j in centroids_new:
                # centroid new get [Xn, Yn]
                centroid_new_instance = centroids_new[j]
                
                centroid_old_instance_distances.append(
                    self.distance_two_centroids_calculate(
                        centroid_old_instance,
                        centroid_new_instance
                    )
                )
                
                distances_centroids_old_centroids_new[i] = \
                    centroid_old_instance_distances

        return distances_centroids_old_centroids_new

    def indices_new_centroids_from_distances(self,
                                             centroids_old,
                                             centroids_new):
        """
        This method uses following previous methods:
            self.distances_dict_from_old_centroids_and_new_centroids_calculate
            self.new_centroids_assignment_from_min_distances_double_check
        
        For each old centroid, get the index value of
        the centroids new dictionary from the new centroid
        with the smallest distance from the old centroid.

        If all distances from an old centroid to the new centroids
        are larger than a threshold, the second parameter of the
        return tuple is set to False, thus representing the inability
        to assign a new box.
        
        Note: old_centroids and new_centroids must be dictionaries of format
        centroids = {0: [X0, Y0], 1: [X1, Y1], ..., n: [Xn, Yn]}        
        """
        distances = \
            self.distances_dict_from_old_centroids_and_new_centroids_calculate(
                centroids_old, centroids_new
            )

        centroids_new_indices_for_old_centroid = {}
                
        centroids_new_indices = []
        for centroid_index in centroids_new:
            centroids_new_indices.append(centroid_index)
        
        for i in distances:
            min_distance = min(distances[i])
            
            index = centroids_new_indices[distances[i].index(min_distance)]
            
            if min_distance <= self.distanceThreshold:
                
                centroids_new_indices_for_old_centroid[i] = [min_distance,
                                                             True,
                                                             index]
            else:
                centroids_new_indices_for_old_centroid[i] = [min_distance,
                                                             False,
                                                             index]

        return centroids_new_indices_for_old_centroid

    def new_centroids_assignment_from_min_distances_double_clean(
            self, centroids_old, centroids_new):
        """
        This method checks if within the calculated distances for each
        old centroid to new centroids, it occurs that two old centroids
        were assigned the same new centroid.
        
        Args:
            centroids = {0: [X0, Y0], 1: [X1, Y1], ..., n: [Xn, Yn]}
        
        Returns:
            Dict 
        
        Note: old_centroids and new_centroids must be dictionaries of format
        centroids = {0: [X0, Y0], 1: [X1, Y1], ..., n: [Xn, Yn]}       
        """
        centroids_new_indices_for_old_centroid = \
            self.indices_new_centroids_from_distances(
                centroids_old, centroids_new
            )
        
        old_indices = []
        new_indices = []

        for old_centroid_index in centroids_new_indices_for_old_centroid:
            old_indices.append(
                old_centroid_index
            )
            new_indices.append(
                centroids_new_indices_for_old_centroid[old_centroid_index][2]
            )

        doubles = [i for i in set(new_indices) if new_indices.count(i) > 1]
        doubles_assigned = {}

        for j in doubles:
            
            old_index_list_for_doubles = []
            for old_index in old_indices:
                if new_indices[old_indices.index(old_index)] == j:
                    
                    old_index_list_for_doubles.append(old_index)
                else:
                    pass                    
            doubles_assigned[j] = old_index_list_for_doubles

        for new_index_double in doubles_assigned:
            old_indices_distances = []
            old_id = []
            for old_indices in doubles_assigned[new_index_double]:
                centroids_new_indices_for_old_centroid[old_indices][1] = False
                distance = \
                    centroids_new_indices_for_old_centroid[old_indices][0]
                old_indices_distances.append(distance)
                old_id.append(old_indices)

            # Note the limitation of the following method, because
            # the 'min' method only returns the first minimal value of a list.
        
            selected_id = old_id[old_indices_distances.index(
                min(old_indices_distances)
            )]
            centroids_new_indices_for_old_centroid[selected_id][1] = True
      
        return centroids_new_indices_for_old_centroid

    def old_centroids_number_slides_deregistered_check(
            self, new_centroids_sorted_by_distance):
        """
        This method checks how many slides one prediction has been
        deregistered. If the prediction has been deregistered for more
        than a threshold number of slides, the prediction is deleted from
        the self.prediction_IDs_display_current. If not, the counter
        self.prediction_IDs_deregistered is incremented by one for each
        deregistered image.
        
        Parameters
        ----------
            new_centroids_sorted_by_distance: DICT
                        {x: [distance, registered, new_center_index],
                        y: [distance, registered, new_center_index],
                        ...
                        n: [distance, registered, new_center_index]}
                (output of
                self.new_centroids_assignment_from_min_distances_double_clean)
        """
        dict_new_centroids_sorted_by_distance = \
            new_centroids_sorted_by_distance
        to_delete = []
        for centroid_id in new_centroids_sorted_by_distance:
            if not new_centroids_sorted_by_distance[centroid_id][1]:
                print('##### New embryo unregistered. #####')
                count_slides_deregistered = \
                    self.prediction_IDs_deregistered[centroid_id]
    
                if count_slides_deregistered < \
                        self.prediction_slides_deregistered_threshold:
                    self.prediction_IDs_deregistered[centroid_id] += 1
                else:
                    to_delete.append(centroid_id)
            else:
                self.prediction_IDs_deregistered[centroid_id] = 0
                pass
            
        for centroid_to_delete in to_delete:
            del dict_new_centroids_sorted_by_distance[centroid_to_delete]
            self.prediction_IDs_display_current.remove(centroid_to_delete)
            
        return dict_new_centroids_sorted_by_distance

    def new_centroids_not_assigned_add(self,
                                       new_centroids_sorted_by_distance,
                                       centroids_new):
        """
        This method checks if all new predicted centroids
        have been assigned. If yes, the dict which assigns
        old to new centroids will be returned. Else if not,
        the new predicted centroids which have not been
        assigned yet will be added to this list with new indices
        starting from self.prediction_ID_next_usable.
        """
        centroids_new_indices = []
        centroids_assigned_indices = []
        centroids_not_assigned = []

        for centroid_index in centroids_new:
            centroids_new_indices.append(centroid_index)

        for centroid_old in new_centroids_sorted_by_distance:
            centroid_assigned = \
                new_centroids_sorted_by_distance[centroid_old][2]
            centroids_assigned_indices.append(centroid_assigned)
            
        for centroid_new in centroids_new_indices:
            if centroid_new in centroids_assigned_indices:
                pass
            else:
                centroids_not_assigned.append(centroid_new)

        # Here we check how many new centroids have not been assigned yet.
        # If there are any not assigned new centroids, first determine their 
        # new indices based on self.prediction_ID_next_usable.
        # Following, initialize their values both in the object variables,
        # as defined in the __init__ method, as well as in the
        # centroids' dictionary. Last, increment for each added predicted
        # centroid the value for the next free index in
        # self.prediction_ID_next_usable, if new centroids join.

        if len(centroids_not_assigned) == 0:
            pass
        else:
            for centroid_not_assigned in centroids_not_assigned:
                new_index = self.prediction_ID_next_usable
                self.prediction_IDs_display_current.append(new_index)
                self.prediction_IDs_deregistered[new_index] = 0
                new_centroids_sorted_by_distance[new_index] = \
                    [0.0, True, centroid_not_assigned]
                
                self.prediction_ID_next_usable += 1
        
        return new_centroids_sorted_by_distance

    @staticmethod
    def old_centroids_new_centroids_assign(new_centroids_sorted_by_distance,
                                           predictions_old,
                                           predictions_new):
        """
        This method assigns the new predictions to the old indices.
        
        Args:
            new_centroids_sorted_by_distance = {x: [distance,
                                                    registered,
                                                    new_index]}
            predictions_old = {x: [prediction_score, prediction_class,
                                   [ymin, xmin, ymax, xmax]] }
            predictions_new = {x: [prediction_score, prediction_class,
                                   [ymin, xmin, ymax, xmax]] }
        """
        predictions_traced = {}
        
        for centroid_to_assign in new_centroids_sorted_by_distance:
            _, registered, new_index = \
                new_centroids_sorted_by_distance[centroid_to_assign]
            if registered:
                predictions_traced[centroid_to_assign] = \
                    predictions_new[new_index]
            else:
                predictions_traced[centroid_to_assign] = \
                    predictions_old[centroid_to_assign]
                
        return predictions_traced

    def object_track(self, predictions_old, predictions_new):
        """
        This method presupposes that the first method,
        'object_tracking_initialize', was run before, to set up
        possible dependencies. Following, this method runs the
        above methods in a sequence.

        Args:
            predictions = {x: [prediction_score, prediction_class,
                               [ymin, xmin, ymax, xmax]]}
            
        Returns:
            predictions_traced = {x: [prediction_score, prediction_class,
                                      [ymin, xmin, ymax, xmax]]}
        """
        # Initialize first set of predictions and by that necessary variables
        # self.object_tracking_initialize(predictions_old)
        
        # From both initial and subsequent predictions,
        # calculate the centroids of the bounding boxes
        # Format: centroids = {0: [X0, Y0], 1: [X1, Y1], ..., n: [Xn, Yn]}
        
        centroids_old = self.predictions_to_centroids_convert(predictions_old)
        centroids_new = self.predictions_to_centroids_convert(predictions_new)

        # For each initial centroid, calculate the distances to all
        # subsequent centroids. For each initial centroid, retain
        # for the closest subsequent centroid its distance and
        # respective index in new_centroids for all centroids,
        # check if any old_centroids have been assigned the same new_centroid,
        # and keep the assignment for the old_centroid with the shortest
        # distance to  the new centroid Format: centroids_allocations
        # = {n: [min_distance <float>,
        #        registered <boolean>,
        #        index_of_allocated_new_centroid <int>]
        centroids_allocations = \
            self.new_centroids_assignment_from_min_distances_double_clean(
                centroids_old,
                centroids_new
            )

        # For all initial centroids, check if active, else deregister.
        # Format: centroids_allocations_deregistered
        # = {n: [min_distance <float>,
        #        registered <boolean>,
        #        index_of_allocated_new_centroid <int>]
        centroids_allocations_deregistered = \
            self.old_centroids_number_slides_deregistered_check(
                centroids_allocations
            )

        # For all subsequent centroids, check if assigned to initial centroid,
        # else assign new. Format:
        # centroids_allocations_deregistered_following_registered =
        #     {n: [min_distance <float>,
        #          registered <boolean>,
        #          index_of_allocated_new_centroid <int>]
        #  }
        centroids_allocations_deregistered_following_registered = \
            self.new_centroids_not_assigned_add(
                centroids_allocations_deregistered,
                centroids_new
            )
        
        # For all registered centroids, assign the following prediction,
        # if still registered, or the initial prediction, if not
        # registered and not excluded yet. Format:
        # predictions_traced = {x: [prediction_score, prediction_class,
        #                           [ymin, xmin, ymax, xmax]]}
        predictions_traced = self.old_centroids_new_centroids_assign(
            centroids_allocations_deregistered_following_registered,
            predictions_old,
            predictions_new
        )
                                                                  
        return predictions_traced

    def object_track_light(self, predictions_old, predictions_new):
        """
        Method to only calculate new prediction indices through distance.
        """
        centroids_old = self.predictions_to_centroids_convert(predictions_old)
        centroids_new = self.predictions_to_centroids_convert(predictions_new)
        centroids_allocations = \
            self.new_centroids_assignment_from_min_distances_double_clean(
                centroids_old,
                centroids_new
            )
        
        predictions_traced = self.old_centroids_new_centroids_assign(
            centroids_allocations,
            predictions_old,
            predictions_new
        )
                                                                  
        return predictions_traced
