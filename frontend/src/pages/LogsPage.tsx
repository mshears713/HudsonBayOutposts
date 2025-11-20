/**
 * Expedition Logs Page Component
 *
 * Displays all expedition logs
 */

import React from 'react';
import ExpeditionLogList from '../components/ExpeditionLogList';

const LogsPage: React.FC = () => {
  return (
    <div>
      <ExpeditionLogList />
    </div>
  );
};

export default LogsPage;
