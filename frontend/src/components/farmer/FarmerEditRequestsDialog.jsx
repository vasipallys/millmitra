import React, { useState } from 'react';
import {
  Dialog, DialogTitle, DialogContent, DialogActions,
  Button, Typography, Box, Chip, Card, CardContent,
  Grid, Divider, TextField, Alert, IconButton,
  Accordion, AccordionSummary, AccordionDetails,
  List, ListItem, ListItemText, ListItemIcon
} from '@mui/material';
import {
  ExpandMore, CheckCircle, Cancel, Schedule,
  Person, Phone, Email, LocationOn, AccountBalance,
  Agriculture, Info, Warning, Flag
} from '@mui/icons-material';
import { useQuery, useMutation, useQueryClient } from 'react-query';
import { farmerService } from '../../services/farmerService';

const FarmerEditRequestsDialog = ({ open, onClose, farmerId = null }) => {
  const [selectedRequest, setSelectedRequest] = useState(null);
  const [reviewComments, setReviewComments] = useState('');
  const [reviewError, setReviewError] = useState('');
  const [reviewAction, setReviewAction] = useState(null); // 'approve' or 'reject'
  
  const queryClient = useQueryClient();

  // Fetch edit requests
  const { data: editRequestsData, isLoading } = useQuery(
    ['farmer-edit-requests', farmerId],
    () => farmerService.getEditRequests(farmerId ? { farmer_id: farmerId } : { status: 'pending' }),
    {
      enabled: open,
      refetchOnWindowFocus: false
    }
  );

  // Approve edit request mutation
  const approveRequestMutation = useMutation(
    ({ requestId, comments }) => farmerService.approveEditRequest(requestId, comments),
    {
      onSuccess: () => {
        queryClient.invalidateQueries(['farmer-edit-requests']);
        queryClient.invalidateQueries(['farmers']);
        setSelectedRequest(null);
        setReviewComments('');
        setReviewAction(null);
      }
    }
  );

  // Reject edit request mutation
  const rejectRequestMutation = useMutation(
    ({ requestId, comments }) => farmerService.rejectEditRequest(requestId, comments),
    {
      onSuccess: () => {
        queryClient.invalidateQueries(['farmer-edit-requests']);
        setSelectedRequest(null);
        setReviewComments('');
        setReviewAction(null);
      }
    }
  );

  const editRequests = editRequestsData?.edit_requests || [];

  const getStatusColor = (status) => {
    switch (status) {
      case 'pending': return 'warning';
      case 'approved': return 'success';
      case 'rejected': return 'error';
      default: return 'default';
    }
  };

  const getPriorityColor = (priority) => {
    switch (priority) {
      case 'high': return 'error';
      case 'medium': return 'warning';
      case 'low': return 'info';
      default: return 'default';
    }
  };

  const getFieldIcon = (fieldName) => {
    const iconMap = {
      name: <Person />,
      phone: <Phone />,
      email: <Email />,
      village: <LocationOn />,
      district: <LocationOn />,
      state: <LocationOn />,
      bank_account: <AccountBalance />,
      ifsc_code: <AccountBalance />,
      farming_type: <Agriculture />,
      land_area: <Agriculture />
    };
    return iconMap[fieldName] || <Info />;
  };

  const formatFieldName = (fieldName) => {
    return fieldName.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase());
  };

  const handleReviewSubmit = () => {
    if (!selectedRequest || !reviewAction) return;

    if (reviewAction === 'approve') {
      approveRequestMutation.mutate({
        requestId: selectedRequest.id,
        comments: reviewComments
      });
    } else if (reviewAction === 'reject') {
      if (!reviewComments.trim()) {
        setReviewError('Please provide a reason for rejection');
        return;
      }
      rejectRequestMutation.mutate({
        requestId: selectedRequest.id,
        comments: reviewComments
      });
    }
  };

  const renderChangeDetails = (request) => {
    const summary = request.changed_fields || [];
    const originalData = request.original_data || {};
    const proposedChanges = request.proposed_changes || {};

    return (
      <Box>
        <Typography variant="h6" gutterBottom>
          Proposed Changes ({summary.length} fields)
        </Typography>
        
        <List>
          {summary.map((fieldName, index) => (
            <ListItem key={index} divider>
              <ListItemIcon>
                {getFieldIcon(fieldName)}
              </ListItemIcon>
              <ListItemText
                primary={formatFieldName(fieldName)}
                secondary={
                  <React.Fragment>
                    <span style={{ display: 'block', color: 'rgba(0, 0, 0, 0.6)', marginBottom: '4px' }}>
                      <strong>Current:</strong> {originalData[fieldName] || 'Not set'}
                    </span>
                    <span style={{ display: 'block', color: '#1976d2' }}>
                      <strong>Proposed:</strong> {proposedChanges[fieldName] || 'Not set'}
                    </span>
                  </React.Fragment>
                }
              />
            </ListItem>
          ))}
        </List>
      </Box>
    );
  };

  return (
    <Dialog
      open={open}
      onClose={onClose}
      maxWidth="lg"
      fullWidth
      PaperProps={{
        sx: { height: '80vh' }
      }}
    >
      <DialogTitle>
        <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
          <Typography variant="h6">
            {farmerId ? 'Farmer Edit History' : 'Pending Edit Requests'}
          </Typography>
          <Chip
            label={`${editRequests.length} requests`}
            color="primary"
            variant="outlined"
          />
        </Box>
      </DialogTitle>

      <DialogContent dividers>
        {isLoading ? (
          <Typography>Loading edit requests...</Typography>
        ) : editRequests.length === 0 ? (
          <Alert severity="info">
            {farmerId ? 'No edit requests found for this farmer.' : 'No pending edit requests.'}
          </Alert>
        ) : (
          <Grid container spacing={2}>
            {/* Requests List */}
            <Grid item xs={12} md={selectedRequest ? 6 : 12}>
              <Box sx={{ maxHeight: '60vh', overflowY: 'auto' }}>
                {editRequests.map((request) => (
                  <Card
                    key={request.id}
                    sx={{
                      mb: 2,
                      cursor: 'pointer',
                      border: selectedRequest?.id === request.id ? 2 : 1,
                      borderColor: selectedRequest?.id === request.id ? 'primary.main' : 'divider'
                    }}
                    onClick={() => setSelectedRequest(request)}
                  >
                    <CardContent>
                      <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                        <Typography variant="h6">
                          {request.farmer_name} ({request.farmer_code})
                        </Typography>
                        <Box sx={{ display: 'flex', gap: 1 }}>
                          <Chip
                            label={request.status}
                            color={getStatusColor(request.status)}
                            size="small"
                          />
                          <Chip
                            label={request.priority}
                            color={getPriorityColor(request.priority)}
                            size="small"
                            icon={<Flag />}
                          />
                        </Box>
                      </Box>

                      <Typography variant="body2" color="text.secondary" gutterBottom>
                        Requested by: {request.requester_name}
                      </Typography>

                      <Typography variant="body2" gutterBottom>
                        <strong>Reason:</strong> {request.request_reason || 'No reason provided'}
                      </Typography>

                      <Typography variant="body2" color="text.secondary">
                        <strong>Changes:</strong> {request.changed_fields?.length || 0} fields
                      </Typography>

                      <Typography variant="caption" color="text.secondary">
                        Submitted: {new Date(request.created_at).toLocaleString()}
                      </Typography>

                      {request.reviewed_at && (
                        <Typography variant="caption" color="text.secondary" display="block">
                          Reviewed: {new Date(request.reviewed_at).toLocaleString()}
                        </Typography>
                      )}
                    </CardContent>
                  </Card>
                ))}
              </Box>
            </Grid>

            {/* Request Details */}
            {selectedRequest && (
              <Grid item xs={12} md={6}>
                <Card sx={{ height: 'fit-content' }}>
                  <CardContent>
                    <Typography variant="h6" gutterBottom>
                      Request Details
                    </Typography>

                    <Divider sx={{ my: 2 }} />

                    {renderChangeDetails(selectedRequest)}

                    {selectedRequest.review_comments && (
                      <Box sx={{ mt: 2 }}>
                        <Typography variant="h6" gutterBottom>
                          Review Comments
                        </Typography>
                        <Alert severity={selectedRequest.status === 'approved' ? 'success' : 'error'}>
                          {selectedRequest.review_comments}
                        </Alert>
                      </Box>
                    )}

                    {selectedRequest.status === 'pending' && (
                      <Box sx={{ mt: 3 }}>
                        <Typography variant="h6" gutterBottom>
                          Review Request
                        </Typography>
                        
                        <TextField
                          fullWidth
                          multiline
                          rows={3}
                          label="Review Comments"
                          value={reviewComments}
                          onChange={(e) => {
                            setReviewComments(e.target.value);
                            if (reviewError) setReviewError('');
                          }}
                          placeholder={reviewAction === 'reject' ? 'Please provide reason for rejection...' : 'Optional approval comments...'}
                          sx={{ mb: 2 }}
                          error={Boolean(reviewError)}
                          helperText={reviewError}
                        />

                        <Box sx={{ display: 'flex', gap: 1 }}>
                          <Button
                            variant="contained"
                            color="success"
                            startIcon={<CheckCircle />}
                            onClick={() => {
                              setReviewAction('approve');
                              handleReviewSubmit();
                            }}
                            disabled={approveRequestMutation.isLoading}
                          >
                            Approve
                          </Button>
                          <Button
                            variant="contained"
                            color="error"
                            startIcon={<Cancel />}
                            onClick={() => {
                              setReviewAction('reject');
                              handleReviewSubmit();
                            }}
                            disabled={rejectRequestMutation.isLoading || !reviewComments.trim()}
                          >
                            Reject
                          </Button>
                        </Box>
                      </Box>
                    )}
                  </CardContent>
                </Card>
              </Grid>
            )}
          </Grid>
        )}
      </DialogContent>

      <DialogActions>
        <Button onClick={onClose}>Close</Button>
      </DialogActions>
    </Dialog>
  );
};

export default FarmerEditRequestsDialog;
