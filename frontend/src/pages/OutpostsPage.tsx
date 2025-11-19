/**
 * Outposts Page Component
 *
 * Displays list of all Raspberry Pi outposts
 */

import React from 'react';
import OutpostList from '../components/OutpostList';

const OutpostsPage: React.FC = () => {
  return (
    <div>
      <OutpostList />
    </div>
  );
};

export default OutpostsPage;
